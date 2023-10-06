
import csv
import websocket
import json
from binance.client import Client
from binance.enums import KLINE_INTERVAL_1SECOND
from credentials import BINANCE_API_KEY, BINANCE_API_SECRET

# Initialize Binance client
client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)

def save_last_200_candlesticks_to_csv(client, trading_pair="BTCTUSD", interval=KLINE_INTERVAL_1SECOND, filename="candlesticks.csv"):
    # Fetch the last 200 candlesticks
    candlesticks = client.get_historical_klines(trading_pair, interval, "200 seconds ago UTC")
    # Save to CSV
    with open(filename, 'w', newline='') as csvfile:
        candlestick_writer = csv.writer(csvfile, delimiter=',')
        for candlestick in candlesticks:
            candlestick_writer.writerow(candlestick)

def on_message(ws, message):
    # Parse the message
    data = json.loads(message)
    # Extract the candlestick data
    candlestick = data['k']
    # Append to the CSV
    with open("candlesticks.csv", 'a', newline='') as csvfile:
        candlestick_writer = csv.writer(csvfile, delimiter=',')
        candlestick_writer.writerow(candlestick)
    # Remove the oldest data to keep only 200 records
    with open("candlesticks.csv", 'r') as csvfile:
        lines = csvfile.readlines()
        if len(lines) > 200:
            lines = lines[1:]
    with open("candlesticks.csv", 'w') as csvfile:
        csvfile.writelines(lines)

# Save the initial 200 candlesticks
save_last_200_candlesticks_to_csv(client)

# Set up the websocket connection
ws_url = "wss://stream.binance.com:9443/ws/btctusd@kline_1s"
ws = websocket.WebSocketApp(ws_url, on_message=on_message)
ws.run_forever()

