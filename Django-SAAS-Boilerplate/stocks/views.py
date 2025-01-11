from django.shortcuts import redirect, render

from user.models import User
from .models import Watchlist, Sector, Stock
from .calculateView import (compute_sector_indicators,
                            compute_stock_indicators, fetch_sectors,
                            fetch_stocks, update_sector_indicators,
                            update_sectors, update_stock_indicators,
                            update_stocks)
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

def dashboard(request):
    return render(request, 'stocks/dashboard_new.html')

def graph_partial(request):
    return render(request, 'stocks/graph_partial.html')

def sectors(request):
    return render(request, 'stocks/sectors.html')

def stock(request):
    return render(request, 'stocks/stock.html')

def main_alerts(request):
    return render(request, 'stocks/main_alerts.html')

def portfolio(request):
    return render(request, 'stocks/portfolio.html')

def settings(request):
    return render(request, 'stocks/settings.html')

def help(request):  
    return render(request, 'stocks/help.html')

@login_required
def watchlist(request):

    # Get the watchlists for the user again in case a new one was created
    # user_watchlists = Watchlist.objects.filter(user=user)

    # Prepare the watchlist data for rendering
    # watchlists = []
    # for watchlist in user_watchlists:
    #     watchlists.append({
    #         "id": watchlist.id,
    #         "name": watchlist.name,
    #         "count": watchlist.count,
    #     })

    # # Debug prints to verify the watchlist data
    # print(user_watchlists)
    # print(f"Last watchlist: {user_watchlists.last()}")
    
    # watchlist_data = {
    #     "stocks": [
    #         {"symbol": "AAPL", "dates": ["10 Jan", "9 Jan", "8 Jan", "7 Jan", "6 Jan"], "data": ["+2", "+1", "-2", "+3", "+4"]},
    #         {"symbol": "MSFT", "dates": ["10 Jan", "9 Jan", "8 Jan", "7 Jan", "6 Jan"], "data": ["+3", "+0", "+2", "+1", "-1"]},
    #         {"symbol": "GOOGL", "dates": ["10 Jan", "9 Jan", "8 Jan", "7 Jan", "6 Jan"], "data": ["+1", "-1", "+2", "+0", "-3"]},
    #         {"symbol": "AMZN", "dates": ["10 Jan", "9 Jan", "8 Jan", "7 Jan", "6 Jan"], "data": ["+4", "+3", "-2", "+1", "+0"]},
    #         {"symbol": "TSLA", "dates": ["10 Jan", "9 Jan", "8 Jan", "7 Jan", "6 Jan"], "data": ["-1", "+2", "-3", "+3", "+5"]},
    #         {"symbol": "NVDA", "dates": ["10 Jan", "9 Jan", "8 Jan", "7 Jan", "6 Jan"], "data": ["+5", "+2", "+3", "+1", "+0"]},
    #         {"symbol": "META", "dates": ["10 Jan", "9 Jan", "8 Jan", "7 Jan", "6 Jan"], "data": ["+2", "+1", "-1", "+0", "+2"]},
    #         {"symbol": "INTC", "dates": ["10 Jan", "9 Jan", "8 Jan", "7 Jan", "6 Jan"], "data": ["-2", "+1", "+3", "-1", "+2"]},
    #         {"symbol": "AMD", "dates": ["10 Jan", "9 Jan", "8 Jan", "7 Jan", "6 Jan"], "data": ["+4", "+3", "+1", "+2", "-1"]},
    #         {"symbol": "ADBE", "dates": ["10 Jan", "9 Jan", "8 Jan", "7 Jan", "6 Jan"], "data": ["+1", "-1", "+2", "+3", "+4"]},
    #         {"symbol": "CRM", "dates": ["10 Jan", "9 Jan", "8 Jan", "7 Jan", "6 Jan"], "data": ["+3", "+4", "+2", "+0", "-1"]},
    #         {"symbol": "ORCL", "dates": ["10 Jan", "9 Jan", "8 Jan", "7 Jan", "6 Jan"], "data": ["+1", "+2", "+3", "-2", "+1"]},
    #         {"symbol": "CSCO", "dates": ["10 Jan", "9 Jan", "8 Jan", "7 Jan", "6 Jan"], "data": ["+0", "+3", "-1", "+1", "+2"]},
    #         {"symbol": "IBM", "dates": ["10 Jan", "9 Jan", "8 Jan", "7 Jan", "6 Jan"], "data": ["-1", "+2", "+3", "+4", "-2"]},
    #         {"symbol": "SHOP", "dates": ["10 Jan", "9 Jan", "8 Jan", "7 Jan", "6 Jan"], "data": ["+3", "+2", "+1", "+0", "-1"]}
    #     ],
    #     "dates": ["10 Jan", "9 Jan", "8 Jan", "7 Jan", "6 Jan"]
    # }
    
    context = {
        # "watchlists": watchlists,
        # "selected_watchlist": selected_watchlist,
        # "selected_watchlist_data": selected_watchlist_data
    }
    
    return render(request, 'stocks/watchlist/watchlist.html', context)


def custom_watchlist(request, watchlist_id):
    return render(request, 'stocks/watchlist/custom_watchlist.html')

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