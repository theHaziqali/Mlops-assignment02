import requests
import json
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from datetime import datetime
# Replace YOUR_API_KEY with your actual Alpha Vantage API key
url = 'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=AAPL&apikey=7DAKX5A7OSW2STDL'

fig, ax = plt.subplots()
x, y = [], []

line, = ax.plot([], [])
def update_plot(i):
    # Fetch the latest real-time data for AAPL
    response = requests.get(url)
    data = json.loads(response.text)

    # Extract the close price and date from the response
    close_price = float(data['Global Quote']['05. price'])
    date_str = data['Global Quote']['07. latest trading day']
    date = datetime.strptime(date_str, '%Y-%m-%d')
    # Add the close price and date to the plot data
    x.append(date)
    y.append(close_price)

    # Update the line chart with the new data
    line.set_data(x, y)
    ax.relim()
    ax.autoscale_view()

ani = FuncAnimation(fig, update_plot, interval=100)
plt.show()