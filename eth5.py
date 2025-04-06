import ccxt
import pandas as pd
import time
import requests
from ta.trend import MACD
from ta.momentum import RSIIndicator, ROCIndicator

# Initialize Binance API (Public Data)
exchange = ccxt.binance()

# Telegram Bot Credentials
TELEGRAM_BOT_TOKEN = "7247966745:AAFlUUJQ1QHvnawxzZRiZlCMQXQQj2wKRXE"
TELEGRAM_CHAT_ID = "6729902571"

# Function to fetch ETH/USDT historical data
def fetch_crypto_data(symbol="ETH/USDT", timeframe='5m', limit=100):
    bars = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
    df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df

# Function to calculate MACD, RSI, and Momentum
def calculate_indicators(df):
    df['MACD'] = MACD(df['close']).macd()
    df['MACD_Signal'] = MACD(df['close']).macd_signal()
    df['RSI'] = RSIIndicator(df['close']).rsi()
    df['Momentum'] = ROCIndicator(df['close'], window=10).roc()
    return df

# Function to generate Buy/Sell signals
def generate_signal(df):
    latest = df.iloc[-1]
    
    if latest['MACD'] > latest['MACD_Signal'] and latest['RSI'] < 30 and latest['Momentum'] > 0:
        return "BUY"
    
    elif latest['MACD'] < latest['MACD_Signal'] and latest['RSI'] > 70 and latest['Momentum'] < 0:
        return "SELL"
    
    return "HOLD"

# Function to send Telegram Alert
def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    requests.post(url, data=data)

# Main loop (Runs every 1 minute)
while True:
    try:
        data = fetch_crypto_data()
        data = calculate_indicators(data)
        signal = generate_signal(data)
        timestamp = data.iloc[-1]['timestamp']

        if signal == "BUY":
            message = f"🚀 ETH BUY ALERT!\n{timestamp}\n🔹 RSI Below 30\n🔹 Momentum Rising\n🔹 MACD Bullish"
            send_telegram_alert(message)

        elif signal == "SELL":
            message = f"⚠ ETH SELL ALERT!\n{timestamp}\n🔻 RSI Above 70\n🔻 Momentum Falling\n🔻 MACD Bearish"
            send_telegram_alert(message)

        print(f"{timestamp} | ETH/USDT Signal: {signal}")

        time.sleep(60)  # Wait 1 minute before next check

    except Exception as e:
        print(f"Error: {e}")
        time.sleep(60)  # Wait before retrying
