from flask import Flask
import pickle
from flask import Flask, render_template
import pandas as pd
import requests
import json
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

app = Flask(__name__)
# Loading model to compare the results
model = pickle.load(open('model.pkl','rb'))

@app.route('/')
def home():
    # Return the components to the HTML template
    return ("Hello")
@app.route('/predict/')
def predict():
    # Set the OpenAQ API endpoint and parameters
    endpoint = 'https://api.openaq.org/v1/measurements'
    city = 'Beijing'
    parameter = 'pm25'
    date_from = '2022-01-01'
    date_to = '2023-04-25' # modify to include the specific date
    params = {
        'city': city,
        'parameter': parameter,
        'date_from': date_from,
        'date_to': date_to,
        'limit': 10000 # maximum number of results per request
    }
    # Send the API request and retrieve the response
    response = requests.get(endpoint, params=params)

    # Extract the measurement data from the response JSON
    measurements = response.json()['results']

    # Convert the measurement data to a Pandas DataFrame
    df = pd.DataFrame(measurements)

    # Formatting of Coordinated column
    df['latitude'] = df['coordinates'].apply(lambda x: x['latitude'])
    df['longitude'] = df['coordinates'].apply(lambda x: x['longitude'])

    # Date Extraction from datetime
    df['datetime'] = pd.to_datetime(df['date'].apply(lambda x: x['utc']))
    df['date'] = df['datetime'].dt.date

    # Average air quality measurement for each day
    grouped = df.groupby('date').agg({
        'value': 'mean'
    }).reset_index()

    # Convert the date column to datetime format
    grouped['date'] = pd.to_datetime(grouped['date'])

    # Train the linear regression model on the entire dataset
    regressor = LinearRegression()
    regressor.fit(grouped.index.values.reshape(-1, 1), grouped['value'])

    specific_date = '2022-01-15'

    # Get the index value of the specific date in the grouped DataFrame
    specific_date_index = grouped[grouped['date'] == specific_date].index[0]

    # Predict the air quality measurement for the specific date
    specific_date_prediction = regressor.predict([[specific_date_index]])

    # Print the predicted value for the specific date
    print("Predicted air quality measurement for", specific_date, ":", specific_date_prediction[0])

    # Get user input for a specific date
    input_date = input("Enter a specific date (YYYY-MM-DD): ")

    # Predict the air quality measurement for the next day
    input_date_index = grouped[grouped['date'] == input_date].index[0]
    next_day_index = input_date_index + 1
    next_day_prediction = regressor.predict([[next_day_index]])

    # Print the predicted value
    print("Predicted air quality measurement for the next day:", next_day_prediction[0])

    # Plot the data and the predicted value
    plt.plot(grouped.index, grouped['value'], color='blue')
    plt.plot(next_day_index, next_day_prediction[0], marker='o', markersize=8, color='red')
    plt.xlabel('Days')
    plt.ylabel('Average air quality measurement')
    plt.title('Daily average value')
    plt.show()


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0',port=3003)
