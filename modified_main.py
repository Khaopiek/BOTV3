
from analysis import analyze_data
from telegram_message_sender import send_message

print('Bot Script Started...')
send_message('Bot Script Started...')



import websocket
import json
import logging
import telegram
from binance.client import Client

# Importing from credentials.py
from credentials import TELEGRAM_API_KEY, BINANCE_API_KEY, BINANCE_API_SECRET, SEND_TELEGRAM_MESSAGE, TELEGRAM_USER_ID_LIST

# Initialize Binance and Telegram clients
binance_client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)
telegram_bot = telegram.Bot(token=TELEGRAM_API_KEY)

def get_trimmed_quantity(quantity, step_size):
    trimmed_quantity = round(quantity, step_size)
    return trimmed_quantity

def get_trimmed_price(price, tick_size):
    trimmed_price = round(price, tick_size)
    return trimmed_price

# Fetch precision for BTCTUSD (or the asset you're trading)
info = binance_client.futures_exchange_info()
precision_data = next((item for item in info['symbols'] if item["symbol"] == "BTCTUSD"), None)
quantity_precision = precision_data['quantityPrecision']
price_precision = precision_data['pricePrecision']

# Constants
ORDER_PERCENTAGE = 10  # Placeholder value, set to desired percentage

# Define functions to fetch balance and calculate order amount
def get_balance(asset):
    balance = binance_client.get_asset_balance(asset=asset)
    return float(balance['free'])

def calculate_order_amount(balance, percentage):
    return balance * (percentage / 100)

def place_order(symbol, order_type, amount):
    if order_type == "buy":
        order = binance_client.order_market_buy(symbol=symbol, quantity=amount)
    elif order_type == "sell":
        order = binance_client.order_market_sell(symbol=symbol, quantity=amount)
    else:
        print("Invalid order type!")
        return
    return order

# Remaining original code ...


from analysis import analyze_data
from telegram_message_sender import send_message

from telegram_message_sender import send_message


# Your original global variables
# Define the moving averages
MA1 = [1]
MA2 = [50]
MA3 = [200]

# Define the indicators
I1 = 0
I2 = 0
I3 = 0
# Store the last buy transaction details
last_buy_price = 0
last_buy_amount = 0




def on_message(ws, message):
    global MA1, MA2, MA3, I1, I2, I3

    # Analyze the data and get the moving averages
    _, MA1, MA2, MA3 = analyze_data()

    # Calculate indicators
    I1 = 1 if sum(MA1)/len(MA1) > sum(MA2)/len(MA2) else 0
    I2 = 1 if sum(MA2)/len(MA2) > sum(MA3)/len(MA3) else 0
    I3 = 5 if sum(MA1)/len(MA1) < sum(MA3)/len(MA3) else 0

    # Buy logic
    if I1 + I2 + I3 == 2:
        # Fetch the available balance (assuming using USDT for simplicity)
        balance = get_balance("USDT")
        order_amount = calculate_order_amount(balance, ORDER_PERCENTAGE)  # Using the predefined ORDER_PERCENTAGE
        # Truncate the order amount using the fetched precision before placing an order
        order_amount = get_trimmed_quantity(order_amount, quantity_precision)
        order = place_order("BTCTUSD", "buy", order_amount)


        
        # Update the last buy transaction details
last_buy_price = order['fills'][0]['price']
        last_buy_amount = order['fills'][0]['qty']
        
        send_message(f"Buy Signal!\nBought at price: {last_buy_price}\nAmount: {last_buy_amount}")
    
    
# Check if last_buy_price is not 0 before executing sell logic
if 'last_buy_price' in locals() and last_buy_price == 0:
    print("No previous buy order to reference for selling.")
    return


    # Calculate net profit
    net_profit = (close_price - last_buy_price) * last_buy_amount

    # Place market sell order (using a placeholder for symbol and order type for simplicity)
    order = place_order("BTCTUSD", "sell", last_buy_amount)

    send_message(f"Sell Signal!\nBought at price: {last_buy_price}\nSold at price: {close_price}\nAmount: {last_buy_amount}\nNet Profit: {net_profit}")
# Reset the last buy transaction details
        last_buy_price = 0
        last_buy_amount = 0


def on_error(ws, error):
    print(f"Error: {error}")

def on_close(ws, close_status_code, close_msg):
        telegram_bot.sendMessage(chat_id=TELEGRAM_USER_ID_LIST[0], text="Bot has stopped")
print("### closed ###")

def on_open(ws):
    # Subscribe to BTC TUSD 1s interval candlestick data
    ws.send(json.dumps({
        "method": "SUBSCRIBE",
        "params": ["btctusd@kline_1s"],
        "id": 1
    }))

telegram_bot.sendMessage(chat_id=TELEGRAM_USER_ID_LIST[0], text="Bot has started")

ws = websocket.WebSocketApp("wss://stream.binance.com:9443/ws/btctusd@kline_1s",
                            on_message=on_message,
                            on_error=on_error,
                            on_close=on_close)
ws.on_open = on_open

import time

def on_message(ws, message):
    data = json.loads(message)
    if 'id' in data and data['id'] == 'unique_request_id' and 'result' in data:
        kline_data = data['result'][0]
        closing_price = kline_data[4] # Close price from the response structure
        print(f"Closing Price: {closing_price}")
    elif 'e' in data and data['e'] == 'ping':
        # Respond to server pings
        ws.send(json.dumps({"e": "pong"}))

def on_error(ws, error):
    print(f"Error: {error}")

def on_close(ws, close_status_code, close_msg):
    print("WebSocket Closed.")

def on_open(ws):
    # Subscription request
    request = {
        "method": "SUBSCRIBE",
        "params": ["btctusd@kline_1s"],
        "id": 1
    }
    ws.send(json.dumps(request))

# Handling automatic reconnection
def start_websocket():
    ws_endpoint = "wss://stream.binance.com:9443/ws/btctusd@kline_1s"
    ws = websocket.WebSocketApp(ws_endpoint, 
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open
    
    # Keep the connection alive
    while True:
        try:
            ws.run_forever()
        except Exception as e:
            print(f"WebSocket error: {e}. Retrying in 60 seconds.")
            time.sleep(60)

# Start the WebSocket connection
start_websocket()



send_message('Bot Script Ended.')
print('Bot Script Ended.')