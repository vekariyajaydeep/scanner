import pandas as pd
import yfinance as yahooFinance

file_path = 'stocks.csv'
df = pd.read_csv(file_path)


def get_stock_data(symbol, period="1y"):
    ticker = yahooFinance.Ticker(symbol)
    return ticker.history(period=period)


def get_last_3_days(data):
    return data.tail(3)


def calculate_ema(data, span):
    return data['Close'].ewm(span=span, adjust=False).mean()


def check_criteria(data, ema_9, ema_20, high_52_week):
    if len(data) < 3:
        return False
    close_3_days_ago = data['Close'].iloc[0]
    close_2_days_ago = data['Close'].iloc[1]
    close_today = data['Close'].iloc[2]
    open_today = data['Open'].iloc[2]

    percent_increase = (close_2_days_ago - close_3_days_ago) / close_3_days_ago * 100

    # Check if the last day is a red candle and movement is <= 2% from the previous day's close
    red_candle = close_today < open_today
    movement_percent = abs((close_today - close_2_days_ago) / close_2_days_ago) * 100
    candle_movement_check = movement_percent <= 2

    # Check if the second candle closes above EMA(9) and EMA(20) by at least 3%
    ema_9_value = ema_9.iloc[-2]
    ema_20_value = ema_20.iloc[-2]

    close_above_ema_9 = close_2_days_ago > ema_9_value * 1.03
    close_above_ema_20 = close_2_days_ago > ema_20_value * 1.03

    # Check if today's close is not higher than the 52-week high
    close_below_52_week_high = close_today <= high_52_week

    return (percent_increase >= 3 and red_candle and candle_movement_check
            and close_above_ema_9 and close_above_ema_20 and close_below_52_week_high)


# File to save the results
output_file = 'screened_stocks.txt'

with open(output_file, 'w') as file:
    for symbol in df['SYMBOL']:
        print(f"Fetching data for {symbol}...")
        data = get_stock_data(symbol)
        if data.empty or len(data) < 3:
            print(f"No sufficient data found for {symbol}")
            continue

        # Calculate EMA(9) and EMA(20)
        ema_9 = calculate_ema(data, 9)
        ema_20 = calculate_ema(data, 20)

        # Calculate 52-week high
        high_52_week = data['High'].max()

        last_3_days_data = get_last_3_days(data)
        if check_criteria(last_3_days_data, ema_9, ema_20, high_52_week):
            result = f" {symbol} meets the criteria"
            print(result)
            file.write(symbol + '\n')

print(f"\nScreening results have been saved to {output_file}.")
