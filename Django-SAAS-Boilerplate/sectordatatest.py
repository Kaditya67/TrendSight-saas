# Import yfinance library
import yfinance as yf

# Define stock symbol and date range
stock = {'symbol': '^CNXAUTO'}  # Example stock symbol
start_date = '2023-01-01'
end_date = '2023-12-31'

# Download stock data
df_new = yf.download(stock['symbol'], start=start_date, end=end_date)

# Display the downloaded data
print(df_new)
print(stock['symbol'])
