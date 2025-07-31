from flask import Flask, render_template, request, redirect, url_for, flash,session
import mysql.connector
import os
import pickle
secret_key = os.urandom(24)

app = Flask(__name__)
# app.secret_key = "your_secret_key"
app.secret_key = secret_key


model=pickle.load(open("model.pkl","rb"))

# MySQL Configuration
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "database": "demo"
}

# Function to establish a database connection
def get_db_connection():
    return mysql.connector.connect(**db_config)

# Routes
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/predict', methods=['GET', 'POST'])
def predict():
    # Retrieve form data
    area = float(request.form['area'])
    bedrooms = int(request.form['bedrooms'])
    bathrooms = int(request.form['bathrooms'])
    stories = int(request.form['stories'])
    mainroad = int(request.form['mainroad'])
    parking = int(request.form['parking'])
    furnishingstatus = int(request.form['furnishingstatus'])
    price_per_sqft = float(request.form['price_per_sqft'])

    # Perform prediction
    prediction = model.predict([[area, bedrooms, bathrooms, stories, mainroad, parking, furnishingstatus, price_per_sqft]])
    output = round(prediction[0], 2)
    output = float(output) 

    # Save input data and prediction to the database
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("INSERT INTO prediction_data (area, bedrooms, bathrooms, stories, mainroad, parking, furnishingstatus, Price_per_sqft,price) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                       (area, bedrooms, bathrooms, stories, mainroad, parking, furnishingstatus, price_per_sqft, output))
        connection.commit()
    except mysql.connector.Error as err:
        print("Error:", err)
        connection.rollback()
        print("MySQL Error:", err.msg)  # Print the error message
        print("MySQL Error Code:", err.errno)  # Print the error code

    cursor.close()
    connection.close()

    return render_template('index.html', prediction_text=f'Total Price of house is : ₹{output}/-')


if __name__ == '__main__':
    app.run(debug=True)
    