from django.shortcuts import render

# Create your views here.
def index(request):
    if request.user.is_authenticated:
        logged=True
    else:
        logged=False
    context = {
        'logged': logged
    }
    return render(request, 'stocks/index.html',context)

def user_login(request):
    return render(request, 'stocks/user_login.html')

def nuser_logout(request):
    return render(request, 'stocks/logout.html')

def subscription(request):
    return render(request, 'stocks/subscription.html')

def forget_password(request):
    return render(request, 'stocks/forgetpassword.html')

def signup(request):
    return render(request, 'stocks/signup.html')

def dashboard(request):
    return render(request, 'stocks/dashboard.html')

def graph_partial(request):
    return render(request, 'stocks/graph_partial.html')

def sectors(request):
    return render(request, 'stocks/sectors.html')

def stocks(request):
    return render(request, 'stocks/stocks.html')

def main_alerts(request):
    return render(request, 'stocks/main_alerts.html')

def portfolio(request):
    return render(request, 'stocks/portfolio.html')

def settings(request):
    return render(request, 'stocks/settings.html')

def help(request):  
    return render(request, 'stocks/help.html')

def watchlist(request):
    return render(request, 'stocks/watchlist.html')

def about(request):
    return render(request, 'stocks/about.html')


from .models import Stock, FinancialStockData 
import yfinance as yf
from datetime import datetime, timedelta
import logging
import pandas_datareader as pdr

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
    stocks = Stock.objects.values_list('symbol', 'id')

    for stock_symbol, stock_id in stocks: 
        end_date = datetime.now()
        start_date = end_date - timedelta(days=700)

        print(f"Fetching data for {stock_symbol} (ID: {stock_id})")

        try:
            df_new = yf.download(stock_symbol, start=start_date, end=end_date)
 
            if df_new.empty:
                print(f"No data found for {stock_symbol}")
                continue

            print(df_new)
 
            for idx, row in df_new.iterrows():
                FinancialStockData.objects.create(
                    stock_id=stock_id,
                    date=row.name.date(),  
                    open=row['Open'],
                    high=row['High'],
                    low=row['Low'],
                    close=row['Close'],
                    volume=row['Volume']
                )
        except Exception as error:
            print(f"Error fetching data for {stock_symbol}: {error}")
    return render(request, 'stocks/stockData/fetch_stocks.html')

import pandas as pd
import numpy as np
from django.shortcuts import render
from stocks.models import Stock, FinancialStockData, ComputedStockData

def compute_stock_indicators(request):
    print("compute/stock_indicators/ running!!")
    
    # Fetch first two stock symbols for testing
    symbols = Stock.objects.values_list('symbol', 'id')

    for symbol, stock_id in symbols:
        print(f"Computing indicators for {symbol}")

        # Fetch stock data for the symbol
        stock_data = FinancialStockData.objects.filter(stock__symbol=symbol).order_by('date')
        if not stock_data.exists():
            print(f"No data available for {symbol}")
            continue

        # Convert QuerySet to DataFrame for processing
        df = pd.DataFrame(list(stock_data.values('date', 'close', 'volume')))
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)

        # Ensure the DataFrame has a sequential integer index
        df.reset_index(drop=False, inplace=True)  # Keep 'date' as a column (instead of index)

        # Check if we have enough data (at least 14 rows)
        if len(df) < 14:
            print(f"Not enough data for {symbol} (less than 14 days). Skipping.")
            continue

        # Calculate RSI
        df['change'] = df['close'].diff()
        df['gain'] = np.where(df['change'] > 0, df['change'], 0)
        df['loss'] = np.where(df['change'] < 0, -df['change'], 0)

        # Calculate average gain and loss
        df['avg_gain'] = 0.0  # Make sure it's float
        df['avg_loss'] = 0.0  # Make sure it's float

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
        df['volume50'] = df['volume'].rolling(window=50).mean()

        # Store all computed rows for the stock in ComputedStockData
        for index, row in df.iterrows():
            ComputedStockData.objects.create(
                stock_id=stock_id,
                date=row['date'],  # Use the actual date from the 'date' column
                rs=row['rs'],
                rsi=row['rsi'],
                ema10=row['ema10'],
                ema20=row['ema20'],
                ema30=row['ema30'],
                ema50=row['ema50'],
                ema100=row['ema100'],
                ema200=row['ema200'],
                volume20=str(row['volume20']),  # Convert to string if necessary
                volume50=str(row['volume50']),  # Convert to string if necessary
            )

    print("Stock indicators computation complete!")
    return render(request, 'stocks/stockData/compute_stock_indicators.html')



def update_stocks(request):
    # Override pandas datareader with yfinance
    yf.pdr_override()
    
    # Fetch all stock symbols and ids from the database
    stocks = Stock.objects.values_list('symbol', 'id')

    end_date = datetime.now()
    for stock_symbol, stock_id in stocks: 

        print(f"Fetching data for {stock_symbol} (ID: {stock_id})")

        try:
            # Get the last updated date
            last_updated = FinancialStockData.objects.filter(stock__symbol=stock_symbol).order_by('-date').first()

            if last_updated:
                start_date = last_updated.date + timedelta(days=1)
            else:
                start_date = end_date - timedelta(days=700)  # Fetch 2 year of data if no data found

            update = False
            if last_updated and last_updated.date == end_date.date():
                update = True
                start_date = last_updated.date
                print(f"Updating data for {stock_symbol}")

            # Download stock data
            df_new = yf.download(stock_symbol, start=start_date, end=end_date)
 
            if df_new.empty:
                print(f"No data found for {stock_symbol}")
                continue

            # Delete outdated data if updating
            if update:
                FinancialStockData.objects.filter(stock__symbol=stock_symbol, date__gte=start_date).delete()
                
            # Insert new data
            for idx, row in df_new.iterrows():
                FinancialStockData.objects.create(
                    stock_id=stock_id,
                    date=row.name.date(),  
                    open=row['Open'],
                    high=row['High'],
                    low=row['Low'],
                    close=row['Close'],
                    volume=row['Volume']
                )

        except Exception as error:
            print(f"Error fetching data for {stock_symbol}: {error}")
    
    # Optionally, pass data back to the template (e.g., success message, processed stock symbols)
    return render(request, 'stocks/stockData/update_stocks.html', {'status': 'Stock data update completed.'})

def update_stock_indicators(request):
    print("compute/stock_indicators/ running!!")
    
    # Fetch first two stock symbols for testing
    symbols = Stock.objects.values_list('symbol', 'id')

    for symbol, stock_id in symbols:
        print(f"Computing indicators for {symbol}")

        # Fetch stock data for the symbol
        stock_data = FinancialStockData.objects.filter(stock__symbol=symbol).order_by('date')
        if not stock_data.exists():
            print(f"No data available for {symbol}")
            continue

        # Convert QuerySet to DataFrame for processing
        df = pd.DataFrame(list(stock_data.values('date', 'close', 'volume')))
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)

        # Ensure the DataFrame has a sequential integer index
        df.reset_index(drop=False, inplace=True)  # Keep 'date' as a column (instead of index)

        # Check if we have enough data (at least 14 rows)
        if len(df) < 14:
            print(f"Not enough data for {symbol} (less than 14 days). Skipping.")
            continue

        # Calculate RSI
        df['change'] = df['close'].diff()
        df['gain'] = np.where(df['change'] > 0, df['change'], 0)
        df['loss'] = np.where(df['change'] < 0, -df['change'], 0)

        # Calculate average gain and loss
        df['avg_gain'] = 0.0  # Make sure it's float
        df['avg_loss'] = 0.0  # Make sure it's float

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
        df['volume50'] = df['volume'].rolling(window=50).mean()

        # Store all computed rows for the stock in ComputedStockData
        for index, row in df.iterrows():
            ComputedStockData.objects.create(
                stock_id=stock_id,
                date=row['date'],  # Use the actual date from the 'date' column
                rs=row['rs'],
                rsi=row['rsi'],
                ema10=row['ema10'],
                ema20=row['ema20'],
                ema30=row['ema30'],
                ema50=row['ema50'],
                ema100=row['ema100'],
                ema200=row['ema200'],
                volume20=str(row['volume20']),  # Convert to string if necessary
                volume50=str(row['volume50']),  # Convert to string if necessary
            )

    print("Stock indicators computation complete!")
    return render(request, 'stocks/stockData/compute_stock_indicators.html')