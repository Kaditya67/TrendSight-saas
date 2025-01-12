import yfinance as yf
from django.core.management.base import BaseCommand
import pandas as pd
from datetime import datetime, timedelta
import pandas_datareader as pdr

class Command(BaseCommand):
    help = "Fetch stock data from Yahoo Finance for the last 400 records and save to CSV"

    def handle(self, *args, **kwargs):
        yf.pdr_override()
        result_data = []
        symbol = 'MARUTI.NS'  # Symbol for the stock you want to fetch
        end_date = datetime.now()
        start_date = end_date - timedelta(days=400)  # Fetch data for the last 400 days

        try:
            df_new = yf.download(symbol, start=start_date, end=end_date)
            print(df_new)

            # for idx, row in df_new.iterrows():
            #     result_data.append({
            #         'symbol': symbol,
            #         'date': row.name,
            #         'close_price': row['Close'],
            #     })

        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")

        return result_data
