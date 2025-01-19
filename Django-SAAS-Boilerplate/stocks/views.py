from django.shortcuts import redirect, render
from .calculateView import (compute_sector_indicators,
                            compute_stock_indicators, fetch_sectors,
                            fetch_stocks, update_sector_indicators,
                            update_sectors, update_stock_indicators,
                            update_stocks)
from .featureViews import (custom_watchlist, watchlist, stock, sectors, custom_portfolio)
from .forms import UserProfileForm

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

def countDay():
    pass

from django.shortcuts import render
import json
def dashboard(request):
    countDay()
    # Hardcoded EMA trends data

    ema_trends = {
        '10_ema': 3,
        '20_ema': -2,
        '30_ema': 5,
        '50_ema': 8,
        '100_ema': 12,
        '200_ema': -18,
    }

    sector_data_table = [
        {'name': 'IT', 'days': 5, 'ema_10': 3, 'ema_20': -1, 'ema_30': 4, 'ema_50': 7, 'ema_100': 10, 'ema_200': -2},
        {'name': 'Finance', 'days': -2, 'ema_10': -1, 'ema_20': -3, 'ema_30': 1, 'ema_50': 4, 'ema_100': 6, 'ema_200': 0},
        {'name': 'Energy', 'days': 4, 'ema_10': 5, 'ema_20': 2, 'ema_30': 3, 'ema_50': -2, 'ema_100': 1, 'ema_200': -3},
        {'name': 'Pharma', 'days': -4, 'ema_10': -2, 'ema_20': -5, 'ema_30': -3, 'ema_50': 1, 'ema_100': -1, 'ema_200': -4},
        {'name': 'Auto', 'days': 7, 'ema_10': 5, 'ema_20': 6, 'ema_30': 8, 'ema_50': 9, 'ema_100': 12, 'ema_200': 3},
        {'name': 'FMCG', 'days': -3, 'ema_10': -4, 'ema_20': -1, 'ema_30': 1, 'ema_50': -3, 'ema_100': -2, 'ema_200': -1},
        {'name': 'Realty', 'days': 2, 'ema_10': 1, 'ema_20': 4, 'ema_30': 6, 'ema_50': 7, 'ema_100': 5, 'ema_200': 0},
        {'name': 'Metals', 'days': 9, 'ema_10': 7, 'ema_20': 8, 'ema_30': 10, 'ema_50': 12, 'ema_100': 15, 'ema_200': 6},
        {'name': 'Media', 'days': -2, 'ema_10': -1, 'ema_20': -3, 'ema_30': 2, 'ema_50': 4, 'ema_100': 1, 'ema_200': -5},
        # Add more sectors as needed
    ]

    sector_data = [
        {'name': 'IT', 'days': 8},
        {'name': 'Finance', 'days': -2},
        {'name': 'Energy', 'days': 4},
        {'name': 'Pharma', 'days': -4},
        {'name': 'Auto', 'days': 7},
        {'name': 'FMCG', 'days': -3},
        {'name': 'Realty', 'days': 2},
        {'name': 'Metals', 'days': 9},
        {'name': 'Media', 'days': -2},
        {'name': 'Infra', 'days': 6},
        {'name': 'Chemical', 'days': -5},
        {'name': 'Retail', 'days': 3},
        {'name': 'Construction', 'days': 4},
        {'name': 'Telecom', 'days': -2},
        {'name': 'Agri', 'days': 1},
        {'name': 'Education', 'days': 5},
        {'name': 'Healthcare', 'days': -3},
        {'name': 'Logistics', 'days': 2},
        {'name': 'Textiles', 'days': -1},
        {'name': 'Tourism', 'days': 4},
        {'name': 'Entertainment', 'days': 3},
        {'name': 'Aerospace', 'days': 7},
        {'name': 'Shipping', 'days': 1},
        {'name': 'Automotive', 'days': -2},
        {'name': 'Technology', 'days': 6},
        {'name': 'Manufacturing', 'days': 4},
        {'name': 'Food & Beverages', 'days': 3},
        {'name': 'Mining', 'days': -1},
        {'name': 'Biotech', 'days': 0},
        {'name': 'Agriculture', 'days': 2},
        {'name': 'Government', 'days': 5}
    ]

    context = {
        'sector_data_table': sector_data_table,
        'sector_data_json': json.dumps(sector_data),
        'ema_trends': ema_trends,
    }

    return render(request, 'stocks/dashboard/dashboard.html', context)

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

    return render(request, 'stocks/stock_users/profile.html', {'form': form})

def main_page(request):
    return render(request,'stocks/main_page.html')

def sidebar(request):
    return render(request,'stocks/sidebar.html')
def navbarr(request):
    return render(request,'stocks/navbarr.html')