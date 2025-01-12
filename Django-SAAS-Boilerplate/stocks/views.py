from django.shortcuts import redirect, render
from .calculateView import (compute_sector_indicators,
                            compute_stock_indicators, fetch_sectors,
                            fetch_stocks, update_sector_indicators,
                            update_sectors, update_stock_indicators,
                            update_stocks)
from .featureViews import (custom_watchlist, watchlist)
from .models import (Portfolio, Sector, Stock, User, Watchlist,FinancialStockData, SellStocks)
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

from django.shortcuts import redirect
from django.urls import reverse

@login_required
def custom_portfolio(request):
    user = request.user
    msg = ""
    
    if request.method == 'POST':
        print(request.POST)
        stock_id = request.POST.get("stock_id")  # e.g., "Reliance"
        last_purchased_date = request.POST.get("last_purchased_date")  # e.g., "2023-01-01"
        quantity = int(request.POST.get("quantity"))
        average_purchase_price = float(request.POST.get("price_per_share"))  # e.g., 2500.0
        
        # Add the stock to the user's portfolio
        Portfolio.objects.create(
            user=user, 
            stock_id=stock_id, 
            last_purchased_date=last_purchased_date, 
            quantity=quantity, 
            average_purchase_price=average_purchase_price
        )

        # Add a success message (using PRG to avoid re-submission on reload)
        request.session['msg'] = "Stock added to portfolio successfully!"
        return redirect(reverse('custom_portfolio'))  # Redirect to the same view

    # Retrieve the success message from the session and clear it
    msg = request.session.pop('msg', "")

    # Prepare stock list
    stocks = [stock for stock in Stock.objects.all() if len(FinancialStockData.objects.filter(stock=stock)) > 15]

    # Portfolio data
    portfolio_data = []
    total_invested_capital = 0
    for record in Portfolio.objects.filter(user=user):
        total_value = record.quantity * record.average_purchase_price
        total_invested_capital += total_value
        portfolio_data.append({
            "stock": record.stock,
            "last_purchased_date": record.last_purchased_date,
            "quantity": record.quantity,
            "average_purchase_price": record.average_purchase_price,
            "total_value": total_value
        })

    # Sell transactions data
    sell_data = []
    for record in SellStocks.objects.filter(user=user):
        sell_data.append({
            "stock": record.stock,
            "quantity": record.quantity,
            "total_price": record.total_price,
            "last_sell_date": record.last_sell_date,
            "is_profit": record.is_profit,
            "profit_or_loss": record.profit_or_loss
        })

    context = {
        "username": user.name,
        "msg": msg,
        "stocks": stocks,
        "portfolio_data": portfolio_data,
        "sell_data": sell_data,
        "total_invested_capital": total_invested_capital
    }

    return render(request, 'stocks/portfolio/custom_portfolio.html', context)

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