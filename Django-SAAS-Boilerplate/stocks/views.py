from django.shortcuts import redirect, render
from .calculateView import (compute_sector_indicators,
                            compute_stock_indicators, fetch_sectors,
                            fetch_stocks, update_sector_indicators,
                            update_sectors, update_stock_indicators,
                            update_stocks)
from .featureViews import (custom_watchlist, watchlist, stock, sectors, custom_portfolio, stock_chart, charts)
from .forms import UserProfileForm
from django.contrib.auth.decorators import login_required

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

from .models import Sector,SectorFinancialData,ComputedSectorData, sectorIndicatorCount

def countDay():
    for sector in Sector.objects.all():
        # print(f"Computing indicators for {sector.symbol} (ID: {sector.id})")
        emas = [10, 20, 30, 50, 100, 200]
        
        # Initialize stock data dictionary
        stock_data = {
            "symbol": sector.symbol, 
        }

        # Retrieve the stock data and EMA records for the sector
        stock_data_records = SectorFinancialData.objects.filter(sector=sector).order_by('-date')
        stock_ema_records = ComputedSectorData.objects.filter(sector=sector).order_by('-date')
        if len(stock_data_records) < 15 and len(stock_ema_records) < 15:
            print(f"Insufficient data for {sector.symbol}")
            continue
        
        # Initialize lists for each EMA in the stock_data dictionary
        for ema in emas:
            stock_data[f'ema{ema}'] = []

        # Loop through the records and compute EMA counters
        for ema in emas:
            ema_counter = 0
            for record, ema_record in zip(reversed(stock_data_records), reversed(stock_ema_records)): 
                # Access the specific EMA value dynamically
                ema_value = getattr(ema_record, f"ema{ema}")

                # Compare close price with the EMA value
                if record.close > ema_value:
                    ema_counter = ema_counter + 1 if ema_counter >= 0 else 1
                else:
                    ema_counter = ema_counter - 1 if ema_counter <= 0 else -1
                
                # Append the computed EMA counter for this record
            stock_data[f'ema{ema}'].append(ema_counter)

        # Update in the database
        # print(f"{sector.symbol}: EMA10 = {stock_data['ema10']}, EMA20 = {stock_data['ema20']}, "
        #       f"EMA30 = {stock_data['ema30']}, EMA50 = {stock_data['ema50']}, "
        #       f"EMA100 = {stock_data['ema100']}, EMA200 = {stock_data['ema200']}, "
        #       f"Date = {stock_data_records[0].date}")
        sectorIndicatorCount.objects.update_or_create(
            sector=sector,
            defaults={
                'date' : stock_data_records[0].date,
                'ema10Count': stock_data['ema10'][0],
                'ema20Count': stock_data['ema20'][0],
                'ema30Count': stock_data['ema30'][0],
                'ema50Count': stock_data['ema50'][0],
                'ema100Count': stock_data['ema100'][0],
                'ema200Count': stock_data['ema200'][0],
                'last_updated': stock_data_records[0].date
            }
        )
        # print(stock_data)



from django.shortcuts import render
import json

@login_required
def dashboard(request):
    # countDay();           // count for sectors
    # Fetch all data from the database
    data = sectorIndicatorCount.objects.all()

    # Filter the "NIFTY 50" sector from the already fetched data
    ema_trends = next((item for item in data if item.sector.name == "NIFTY 50"), None)

    if ema_trends:
        ema_trends_sector = {
            '10': ema_trends.ema10Count,
            '20': ema_trends.ema20Count,
            '30': ema_trends.ema30Count,
            '50': ema_trends.ema50Count,
            '100': ema_trends.ema100Count,
            '200': ema_trends.ema200Count,
        }
    else:
        ema_trends_sector = None

    # Generate sector data table
    sector_data_table = []
    sector_data = []
    for sector in data:
        sector_data_table.append({
            'name': sector.sector.name,
            'ema_10': sector.ema10Count,
            'ema_20': sector.ema20Count,
            'ema_30': sector.ema30Count,
            'ema_50': sector.ema50Count,
            'ema_100': sector.ema100Count,
            'ema_200': sector.ema200Count,
        })

        sector_data.append({
            'symbol': sector.sector.symbol,
            'name': sector.sector.name,
            'ema_10': sector.ema10Count,
            'ema_20': sector.ema20Count,
            'ema_30': sector.ema30Count,
            'ema_50': sector.ema50Count,
            'ema_100': sector.ema100Count,
            'ema_200': sector.ema200Count,
        })

    context = {
        'sector_data_table': sector_data_table[::-1],
        'sector_data_json': json.dumps(sector_data),
        'ema_trends': ema_trends_sector, 
        'user_avatar': request.user.dp if request.user.dp else None
    }
    # print(context)

    return render(request, 'stocks/dashboard/dashboard.html', context)

def dashboard_new(request):
    return render(request, 'stocks/dashboard_new.html')

def graph_partial(request):
    return render(request, 'stocks/graph_partial.html')



def main_alerts(request):
    return render(request, 'stocks/main_alerts.html')

def portfolio(request):
    return render(request, 'stocks/portfolio.html')

def settings(request):
    return render(request, 'stocks/settings.html')

def help(request):  
    return render(request, 'stocks/help.html')

def add_watchlist(request):
    return render(request,'stocks/watchlist/watchlist.html')

def about(request):
    return render(request, 'stocks/about.html')

def profile(request):
    user = request.user
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile')  # Optionally redirect to profile page after successful save
    else:
        form = UserProfileForm(instance=user)

    return render(request, 'stocks/stock_users/profile.html', {'form': form,'user_avatar': request.user.dp if request.user.dp else None})

def main_page(request):
    return render(request,'stocks/main_page.html')

def sidebar(request):
    return render(request,'stocks/sidebar.html')
def navbarr(request):
    return render(request,'stocks/navbarr.html')