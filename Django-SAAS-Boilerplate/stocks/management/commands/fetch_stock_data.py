import yfinance as yf
from django.core.management.base import BaseCommand
import pandas as pd
from stocks.models import FStockData  # Assuming you have this model for saving stock data

class Command(BaseCommand):
    help = "Fetch stock data from Yahoo Finance"

    def handle(self, *args, **kwargs):
        # Define the date range for data retrieval
        start_date = "2024-10-01"
        end_date = "2024-12-25"

        try:
            # Fetch historical data for Apple Inc. (AAPL) using yfinance
            ticker = yf.Ticker('AAPL')
            print(ticker)
            apple_df = ticker.history(start=start_date, end=end_date)
            print(apple_df)

            # Check if the dataframe is not empty
            if apple_df.empty:
                self.stdout.write(self.style.WARNING('No data returned for the specified range.'))
                return

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error fetching data: {str(e)}"))
