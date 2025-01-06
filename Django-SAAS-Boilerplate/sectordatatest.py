import yfinance as yf

# Example ticker
ticker = yf.Ticker("AAPL")  # Apple Inc.

# Fetch company info
info = ticker.info
print(info.get("sector"))  # Prints the sector (e.g., 'Technology')
print(info.get("industry"))  # Prints the industry (e.g., 'Consumer Electronics')
