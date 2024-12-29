import yfinance as yf
from django.core.management.base import BaseCommand
import pandas as pd
from datetime import datetime, timedelta
import logging

logger = logging.getLogger()
logger.setLevel(logging.WARNING)  # or ERROR to hide less critical logs

class Command(BaseCommand):
    help = "Fetch stock data from Yahoo Finance for the last 400 records and save to CSV"

    def handle(self, *args, **kwargs):
        # Start from today's date
        end_date = datetime.today()  # Use datetime object directly
        total_records = 0
        all_data = []
        batch_size = 30  # You can adjust this based on the number of days per fetch

        try:
            while total_records < 400:
                # Calculate the start date for this batch
                start_date = end_date - timedelta(days=batch_size)

                # Fetch data for the given range
                ticker = yf.Ticker('AAPL')
                print(f"Fetching data for {ticker.info['symbol']} from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
                batch_df = ticker.history(start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'))
                
                if batch_df.empty:
                    self.stdout.write(self.style.WARNING(f"No data returned for {start_date} to {end_date}."))
                    break
                
                # Add the fetched data to the list
                all_data.append(batch_df)
                total_records += len(batch_df)

                # Update the end date to one day before the first date of the fetched data
                end_date = batch_df.index[0] - timedelta(days=1)  # The day before the first date in the batch

                print(f"Fetched {len(batch_df)} records, total so far: {total_records}.")

                # Break if we reach or exceed the target count
                if total_records >= 400:
                    break

            # Combine all fetched data into a single DataFrame
            full_data = pd.concat(all_data).sort_index()

            # Save to CSV
            csv_filename = f"AAPL_stock_data_last_400_records.csv"
            full_data.to_csv(csv_filename)

            self.stdout.write(self.style.SUCCESS(f"Stock data saved to {csv_filename}"))
        
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error fetching data: {str(e)}"))
