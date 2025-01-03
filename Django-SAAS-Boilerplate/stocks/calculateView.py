import logging
from datetime import datetime, timedelta

import numpy as np
import pandas as pd 
import yfinance as yf
from django.shortcuts import render

from stocks.models import (ComputedStockData, FinancialStockData, PrevVolumes,
                           Stock)

from .models import FinancialStockData, Stock

# Suppress informational logs from yfinance, urllib3 and sqlalchemy
logging.getLogger('yfinance').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('sqlalchemy').setLevel(logging.WARNING)

# Suppress unnecessary logs
logging.basicConfig(level=logging.ERROR)
def fetch_stocks(request):
    # Override pandas datareader with yfinance
    yf.pdr_override()
    
    # Fetch all stock symbols and ids from the database
    stocks = Stock.objects.all()
    fetched_data = []  # To store the fetched stock data
    need_update = []   # List to store stocks needing update
    upto_date = []     # List to store up-to-date stocks

    # Helper function to categorize stocks
    def categorize_stocks():
        nonlocal need_update, upto_date
        need_update = []
        upto_date = []
        for stock in stocks:
            try:
                # Fetch the last record of stock data
                last_record = FinancialStockData.objects.filter(stock=stock).last()
                if last_record and last_record.date == datetime.now().date():
                    upto_date.append(stock)  # Stock is up-to-date
                else:
                    need_update.append(stock)  # Stock needs update
            except Exception as e:
                print(f"Error processing stock {stock.symbol}: {e}")
                need_update.append(stock)  # Default to needing update

    # Initial categorization
    categorize_stocks()

    if request.method == 'POST':
        selected_stock_ids = request.POST.getlist('stocks')  # Get list of selected stock IDs
        print(f"Selected Stock IDs: {selected_stock_ids}")
        
        if selected_stock_ids:
            # Fetch selected stocks from the database
            selected_stocks = Stock.objects.filter(id__in=selected_stock_ids).values('symbol', 'id')
            print(f"Selected Stocks: {selected_stocks}")
            
            for stock in selected_stocks: 
                end_date = datetime.now()
                start_date = end_date - timedelta(days=700)

                print(f"Fetching data for {stock['symbol']} (ID: {stock['id']})")

                try:
                    # First, delete existing records for the selected stock symbol
                    FinancialStockData.objects.filter(stock__symbol=stock['symbol']).delete()

                    # Download new stock data
                    df_new = yf.download(stock['symbol'], start=start_date, end=end_date)
        
                    if df_new.empty:
                        print(f"No data found for {stock['symbol']}")
                        continue

                    print(f"Fetched data for {stock['symbol']}: {df_new}")

                    # Prepare a list for bulk creation of stock data
                    stock_data_to_create = []
                    for idx, row in df_new.iterrows():
                        stock_data_to_create.append(
                            FinancialStockData(
                                stock_id=stock['id'],
                                date=row.name.date(),
                                open=row['Open'],
                                high=row['High'],
                                low=row['Low'],
                                close=row['Close'],
                                volume=row['Volume']
                            )
                        )
                    
                    # Bulk create records to improve performance
                    FinancialStockData.objects.bulk_create(stock_data_to_create)

                    # Store the fetched data for displaying in the template
                    for row in df_new.iterrows():
                        fetched_data.append({
                            'symbol': stock['symbol'],
                            'date': row[0].date(),
                            'open': row[1]['Open'],
                            'high': row[1]['High'],
                            'low': row[1]['Low'],
                            'close': row[1]['Close'],
                            'volume': row[1]['Volume']
                        })

                except Exception as error:
                    print(f"Error fetching data for {stock['symbol']}: {error}")

            # Re-categorize stocks after processing the POST request
            categorize_stocks()

        else:
            print("No stocks were selected.")

    context = {
        'stocks': stocks,
        'fetched_data': fetched_data,  # Pass the fetched data to the template
        'need_update': need_update,    # Pass the list of stocks needing update
        'upto_date': upto_date,       # Pass the list of up-to-date stocks
    }
    return render(request, 'stocks/stockData/fetch_stocks.html', context)

def compute_stock_indicators(request):
    print("compute/stock_indicators/ running!!")
    
    # Fetch all stock symbols for testing
    stocks = Stock.objects.all()
    computed_data = []
    no_data = []
    if request.method == 'POST':
        selected_stock_ids = request.POST.getlist('stocks')  # Get list of selected stock IDs
        print(f"Selected Stock IDs: {selected_stock_ids}")
        
        if selected_stock_ids:
            # Fetch selected stocks from the database
            selected_stocks = Stock.objects.filter(id__in=selected_stock_ids).values('symbol', 'id')
            print(f"Selected Stocks: {selected_stocks}")
            
            for stock in selected_stocks: 
                end_date = datetime.now()
                start_date = end_date - timedelta(days=700)

                print(f"Computing indicators for {stock['symbol']} (ID: {stock['id']})")

                try:
                    # Fetch stock data for the symbol
                    stock_data = FinancialStockData.objects.filter(stock__symbol=stock['symbol']).order_by('date')
                    ComputedStockData.objects.filter(stock__symbol=stock['symbol']).delete()
                    if not stock_data.exists():
                        print(f"No data available for {stock['symbol']}")
                        no_data.append(stock['symbol'])
                        continue

                    # Convert QuerySet to DataFrame for processing
                    df = pd.DataFrame(list(stock_data.values('date', 'close', 'volume')))
                    df['date'] = pd.to_datetime(df['date'])
                    df.set_index('date', inplace=True)

                    # Ensure the DataFrame has a sequential integer index
                    df.reset_index(drop=False, inplace=True)

                    # Check if we have enough data (at least 14 rows)
                    if len(df) < 14:
                        print(f"Not enough data for {stock['symbol']} (less than 14 days). Skipping.")
                        continue

                    # Calculate RSI
                    df['change'] = df['close'].diff()
                    df['gain'] = np.where(df['change'] > 0, df['change'], 0)
                    df['loss'] = np.where(df['change'] < 0, -df['change'], 0)

                    # Calculate average gain and loss
                    df['avg_gain'] = 0.0
                    df['avg_loss'] = 0.0

                    # Calculate the first 14-period average gain and loss
                    df.loc[13, 'avg_gain'] = float(df['gain'][:14].mean())
                    df.loc[13, 'avg_loss'] = float(df['loss'][:14].mean())

                    # Use smoothing formula for subsequent rows
                    for i in range(14, len(df)):
                        df.loc[i, 'avg_gain'] = ((df.loc[i - 1, 'avg_gain'] * 13) + df.loc[i, 'gain']) / 14
                        df.loc[i, 'avg_loss'] = ((df.loc[i - 1, 'avg_loss'] * 13) + df.loc[i, 'loss']) / 14

                    # Calculate RS and RSI
                    df['rs'] = df['avg_gain'] / df['avg_loss']
                    df['rsi'] = 100 - (100 / (1 + df['rs']))

                    # Calculate EMAs
                    df['ema10'] = df['close'].ewm(span=10, adjust=False).mean()
                    df['ema20'] = df['close'].ewm(span=20, adjust=False).mean()
                    df['ema30'] = df['close'].ewm(span=30, adjust=False).mean()
                    df['ema50'] = df['close'].ewm(span=50, adjust=False).mean()
                    df['ema100'] = df['close'].ewm(span=100, adjust=False).mean()
                    df['ema200'] = df['close'].ewm(span=200, adjust=False).mean()

                    # Calculate Volume Moving Averages
                    df['volume20'] = df['volume'].rolling(window=20).mean()
                    volume_20th = df['volume'].tail(20).iloc[0]
                    print("Volume 20th : ", volume_20th)

                    df['volume50'] = df['volume'].rolling(window=50).mean()
                    volume_50th = df['volume'].tail(50).iloc[0]
                    print("Volume 50th : ", volume_50th)

                    # Store all computed rows for the stock in ComputedStockData
                    for index, row in df.iterrows():
                        ComputedStockData.objects.create(
                            stock_id=stock['id'],
                            date=row['date'], 
                            rs=row['rs'],
                            rsi=row['rsi'],
                            ema10=row['ema10'],
                            ema20=row['ema20'],
                            ema30=row['ema30'],
                            ema50=row['ema50'],
                            ema100=row['ema100'],
                            ema200=row['ema200'],
                            volume20=str(row['volume20']),
                            volume50=str(row['volume50']),
                        )
                        computed_data.append({
                            'symbol': stock['symbol'],
                            'date': row['date'],
                            'rs': row['rs'],
                            'rsi': row['rsi'],
                            'ema10': row['ema10'],
                            'ema20': row['ema20'],
                            'ema30': row['ema30'],
                            'ema50': row['ema50'],
                            'ema100': row['ema100'],
                            'ema200': row['ema200'],
                            'volume20': str(row['volume20']),
                            'volume50': str(row['volume50']),
                        })

                    # Update volume data for each stock
                    PrevVolumes.objects.update_or_create(
                        stock_id=stock['id'],
                        date=stock_data.last().date,
                        defaults={
                            'volume20': volume_20th,
                            'volume50': volume_50th
                        }
                    )

                except Exception as error:
                    print(f"Error processing stock {stock['symbol']}: {error}")
                    import traceback
                    print("Traceback:", traceback.format_exc())

    context = {
        'stocks': stocks,
        'computed_data': computed_data,
        'no_data': no_data
    }

    print("Stock indicators computation complete!")
    return render(request, 'stocks/stockData/compute_stock_indicators.html', context)

def update_stocks(request):
    # Override pandas datareader with yfinance
    yf.pdr_override()
    end_date = datetime.now()

    # Fetch all stocks from the database
    stocks = Stock.objects.all()
    need_update = []
    upto_date = []

    # Helper function to categorize stocks
    def categorize_stocks():
        nonlocal need_update, upto_date
        need_update = []
        upto_date = []
        for stock in stocks:
            try:
                last_record = FinancialStockData.objects.filter(stock=stock).last()
                if last_record and last_record.date == end_date.date():
                    upto_date.append(stock)
                else:
                    need_update.append(stock)
            except Exception as e:
                print(f"Error processing stock {stock.symbol}: {e}")
                need_update.append(stock)

    # Initial categorization
    categorize_stocks()

    fetched_data = []  # To store the fetched stock data
    msg = f"Stocks separated into Need Update: {len(need_update)} and Upto Date: {len(upto_date)}"
    color = 'red' if len(need_update) > 0 else 'green'

    if request.method == 'POST':
        selected_stock_ids = request.POST.getlist('stocks')  # Get selected stock IDs
        if selected_stock_ids:
            selected_stocks = Stock.objects.filter(id__in=selected_stock_ids)

            for stock in selected_stocks:
                try:
                    # Determine the start date for fetching data
                    last_record = FinancialStockData.objects.filter(stock=stock).last()
                    start_date = last_record.date + timedelta(days=1)  

                    if last_record and last_record.date == end_date.date():
                        start_date = last_record.date
                    print(f"Fetching data for {stock.symbol} from {start_date} to {end_date}")

                    # Download stock data
                    df_new = yf.download(stock.symbol, start=start_date, end=end_date)

                    if df_new.empty:
                        print(f"No data found for {stock.symbol}")
                        continue
                    
                    msg = f"{len(df_new)} records fetched for {stock.symbol}"
                    color = 'green' if len(df_new) > 0 else 'red'
                    # Delete existing data if updating the same dates
                    FinancialStockData.objects.filter(stock=stock, date__gte=start_date).delete()

                    # Save new data
                    for idx, row in df_new.iterrows():
                        FinancialStockData.objects.create(
                            stock=stock,
                            date=row.name.date(),
                            open=row['Open'],
                            high=row['High'],
                            low=row['Low'],
                            close=row['Close'],
                            volume=row['Volume']
                        )
                        fetched_data.append({
                            'symbol': stock.symbol,
                            'date': row.name.date(),
                            'open': row['Open'],
                            'high': row['High'],
                            'low': row['Low'],
                            'close': row['Close'],
                            'volume': row['Volume']
                        })
                except Exception as e:
                    print(f"Error fetching data for {stock.symbol}: {e}")
        else:
            print("No stocks were selected for update.")

        # Re-categorize stocks after processing the POST request
        categorize_stocks()

    context = {
        'fetched_data': fetched_data,
        'status': 'Stock data update completed.' if fetched_data else 'No data updated.',
        'need_update': need_update,
        'uptoDate': upto_date,
        'msg': msg,
        'color': color
    }
    return render(request, 'stocks/stockData/update_stocks.html', context)

def update_stock_indicators(request):
    print("update_stock_indicators/ running!!")
    
    # Fetch stock symbols and IDs
    stocks = Stock.objects.all()
    updated_stocks = []  # List of stocks that were successfully updated
    failed_stocks = []   # List of stocks that failed to update
    need_update = []
    uptoDate = []

    # Helper function to find updated and need_update stocks
    def categorize_stocks():
        need_update = []
        uptoDate = []
        current_date = datetime.now().date()
        for stock in stocks:
            try:
                # Fetch the last record of stock data
                last_record = ComputedStockData.objects.filter(stock=stock).last()
                if last_record and last_record.date == current_date:
                    uptoDate.append(stock)  # Stock is up-to-date
                else:
                    need_update.append(stock)  # Stock needs update
            except Exception as e:
                print(f"Error processing stock {stock.symbol}: {e}")
                need_update.append(stock)
        return need_update, uptoDate            

    if request.method == 'POST':
        selected_stock_ids = request.POST.getlist('stocks')  # Get selected stock IDs
        if selected_stock_ids:
            selected_stocks = Stock.objects.filter(id__in=selected_stock_ids).values('symbol', 'id')

            for stock in selected_stocks:
                
                update_needed = True
                try:
                    print(f"Computing indicators for {stock['symbol']} (ID: {stock['id']})")
                    # Get the last computed record
                    last_computed = ComputedStockData.objects.filter(stock_id=stock['id']).last()
                    last_computed_stock = FinancialStockData.objects.filter(stock_id=stock['id']).last()
                    
                    if last_computed:
                        last_computed_date = last_computed.date
                    else:
                        last_computed_date = None
                    
                    # Compare last computed date with current date
                    current_date = datetime.today().date()
                    
                    if last_computed_date and last_computed_date >= current_date:
                        # If the last computed date is the same as or later than the current date, skip the stock 
                        print(f"No update needed for {stock['symbol']} (last computed: {last_computed_date})")
                        update_needed = False
                        continue

                    # Fetch new stock data
                    stock_data = FinancialStockData.objects.filter(stock_id=stock['id'])
                    if last_computed_date:
                        stock_data = stock_data.filter(date__gt=last_computed_date)

                    if not stock_data.exists():
                        print(f"No new data available for {stock['symbol']} (ID: {stock['id']})")
                        failed_stocks.append(stock['symbol'])  # Add to failed list if no new data
                        continue

                    # Convert new data to DataFrame
                    df_new = pd.DataFrame(list(stock_data.values('date', 'close', 'volume')))
                    df_new['date'] = pd.to_datetime(df_new['date'])
                    df_new.set_index('date', inplace=True)
                    df_new.sort_index(inplace=True)

                    # Initialize previous values
                    prev_rsi = last_computed.rsi if last_computed else 0
                    prev_avg_gain = last_computed.rs * (last_computed.rsi / 100) if last_computed else 0
                    prev_avg_loss = prev_avg_gain / last_computed.rs if last_computed and last_computed.rs > 0 else 0
                    prevVolumes = PrevVolumes.objects.filter(id=stock['id']).last()

                    prev_ema_values = {
                        "ema10": last_computed.ema10 if last_computed else 0,
                        "ema20": last_computed.ema20 if last_computed else 0,
                        "ema30": last_computed.ema30 if last_computed else 0,
                        "ema50": last_computed.ema50 if last_computed else 0,
                        "ema100": last_computed.ema100 if last_computed else 0,
                        "ema200": last_computed.ema200 if last_computed else 0,
                    }

                    computed_data = []
                    for date, row in df_new.iterrows():
                        close = row['close']
                        volume = row['volume']
                        print(f"Processing data for {date} (Close: {close}, Volume: {volume})")

                        # Compute RSI incrementally
                        change = close - (last_computed_stock.close if last_computed else close)
                        gain = max(change, 0)
                        loss = -min(change, 0)

                        avg_gain = (prev_avg_gain * 13 + gain) / 14
                        avg_loss = (prev_avg_loss * 13 + loss) / 14
                        rs = avg_gain / avg_loss if avg_loss > 0 else 0
                        rsi = 100 - (100 / (1 + rs)) 

                        # Compute EMAs incrementally
                        ema_values = {}
                        for span in [10, 20, 30, 50, 100, 200]:
                            key = f"ema{span}"
                            multiplier = 2 / (span + 1)
                            ema_values[key] = (close - prev_ema_values[key]) * multiplier + prev_ema_values[key]

                        prev_volume20 = float(last_computed.volume20) if last_computed else 0
                        prev_volume50 = float(last_computed.volume50) if last_computed else 0
                        volume20 = prev_volume20 + (last_computed_stock.volume - float(prevVolumes.volume20)) / 20
                        volume50 = prev_volume50 + (last_computed_stock.volume - float(prevVolumes.volume50)) / 50

                        computed_data.append(
                            ComputedStockData(
                                stock_id=stock['id'],
                                date=date,
                                rs=rs,
                                rsi=rsi,
                                ema10=ema_values['ema10'],
                                ema20=ema_values['ema20'],
                                ema30=ema_values['ema30'],
                                ema50=ema_values['ema50'],
                                ema100=ema_values['ema100'],
                                ema200=ema_values['ema200'],
                                volume20=str(volume20),
                                volume50=str(volume50),
                            )
                        )

                        updated_stocks.append(computed_data[-1])
                        prev_avg_gain, prev_avg_loss, prev_rsi = avg_gain, avg_loss, rsi
                        prev_ema_values.update(ema_values)

                    # Bulk create new computed data
                    ComputedStockData.objects.bulk_create(computed_data)
                except Exception as error:
                    print(f"Error computing indicators for {stock['symbol']}: {error}")
                    if update_needed:
                        failed_stocks.append(stock['symbol'])  # Add to failed list if error occurs

    # Categorize stocks for processing
    need_update, uptoDate = categorize_stocks()
    context = {
        'stocks': stocks,
        'updated_stocks': updated_stocks,
        'failed_stocks': failed_stocks,
        'need_update': need_update,
        'uptoDate': uptoDate
    }
    return render(request, 'stocks/stockData/update_stock_indicators.html', context)