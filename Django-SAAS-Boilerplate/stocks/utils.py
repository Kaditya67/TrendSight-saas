import requests
from datetime import datetime, timedelta

def fetch_stock_data(symbol):
    """
    Fetch historical stock data from Yahoo Finance using requests.
    """
    try:
        # Define date range
        end_date = int(datetime.now().timestamp())
        start_date = int((datetime.now() - timedelta(days=1)).timestamp())

        # Yahoo Finance URL
        url = f"https://query1.finance.yahoo.com/v7/finance/download/{symbol}"
        params = {
            "period1": start_date,
            "period2": end_date,
            "interval": "1d",
            "events": "history",
        }

        # Fetch data
        response = requests.get(url, params=params)
        if response.status_code != 200:
            print(f"Failed to fetch data for {symbol}: {response.text}")
            return None

        # Parse CSV response
        data = response.text.strip().split("\n")
        headers = data[0].split(",")
        values = data[1].split(",")

        # Map headers to values
        stock_data = dict(zip(headers, values))
        return {
            "symbol": symbol,
            "open": float(stock_data["Open"]),
            "high": float(stock_data["High"]),
            "low": float(stock_data["Low"]),
            "close": float(stock_data["Close"]),
            "volume": int(stock_data["Volume"]),
            "date": stock_data["Date"],
        }

    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None


# Example usage
if __name__ == "__main__":
    stock = fetch_stock_data("AAPL")
    if stock:
        print("Fetched stock data:", stock)
