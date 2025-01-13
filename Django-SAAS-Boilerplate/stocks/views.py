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
from django.contrib import messages
from decimal import Decimal

@login_required
def custom_portfolio(request):
    user = request.user
    msg = ""

    def add_stocks_to_portfolio():
        stock_id = request.POST.get("stock_id")
        last_purchased_date = request.POST.get("last_purchased_date")
        quantity = int(request.POST.get("quantity", 0))
        average_purchase_price = float(request.POST.get("price_per_share", 0.0))

        try:
            # Check if stock already exists in the portfolio
            stock_record = Portfolio.objects.filter(user=user, stock_id=stock_id).first()

            if stock_record:
                # Update the stock quantity and average purchase price
                total_cost = stock_record.quantity * stock_record.average_purchase_price
                new_cost = quantity * Decimal(average_purchase_price)
                total_quantity = stock_record.quantity + quantity

                stock_record.average_purchase_price = (total_cost + new_cost) / total_quantity
                stock_record.quantity = total_quantity
                stock_record.last_purchased_date = last_purchased_date
                stock_record.save()
            else:
                # Add new stock to the portfolio
                Portfolio.objects.create(
                    user=user,
                    stock_id=stock_id,
                    last_purchased_date=last_purchased_date,
                    quantity=quantity,
                    average_purchase_price=average_purchase_price,
                )

            messages.success(request, "Stock added to portfolio successfully!")

        except Exception as e:
            print(e)
            messages.error(request, "An error occurred while updating the portfolio.")
        
        request.session['msg'] = "Stock added to portfolio successfully!"

    def sell_stocks_from_portfolio():
        stock_id = request.POST.get("stock_id")
        last_sell_date = request.POST.get("last_sell_date")
        quantity = int(request.POST.get("quantity", 0))
        price_per_share = Decimal(request.POST.get("price_per_share", 0.0))

        # Ensure the user has enough quantity in their portfolio
        portfolio_entry = Portfolio.objects.filter(user=user, stock_id=stock_id).first()
        if not portfolio_entry or portfolio_entry.quantity < quantity:
            messages.error(request, "Not enough stock quantity to sell.")
            return

        # Calculate profit or loss from this sale
        profit_or_loss_per_unit = Decimal(price_per_share) - Decimal(portfolio_entry.average_purchase_price)
        total_profit_or_loss = profit_or_loss_per_unit * quantity
        is_profit = total_profit_or_loss > 0

        # Update portfolio after selling
        if quantity >= portfolio_entry.quantity:
            # If we are selling all of the stock, delete the portfolio entry
            total_profit_or_loss = (Decimal(price_per_share) - Decimal(portfolio_entry.average_purchase_price)) * portfolio_entry.quantity
            portfolio_entry.delete()  # Remove stock from the portfolio
        else:
            # If we are selling only a part of the stock, update quantity
            portfolio_entry.quantity -= quantity
            portfolio_entry.save()  # Save the reduced quantity

        # Now handle the SellStocks table (where the transaction is recorded)
        stock_record = SellStocks.objects.filter(stock_id=stock_id, user=user).first()

        if stock_record:
            # If a record exists, update the existing record
            old_is_profit = stock_record.is_profit
            old_profit_or_loss = stock_record.profit_or_loss

            if old_is_profit and is_profit:
                stock_record.profit_or_loss += total_profit_or_loss
            elif old_is_profit and not is_profit:
                profit_diff = old_profit_or_loss - total_profit_or_loss
                stock_record.is_profit = profit_diff > 0
                stock_record.profit_or_loss = profit_diff
            elif not old_is_profit and not is_profit:
                stock_record.profit_or_loss += total_profit_or_loss
            else:
                profit_diff = total_profit_or_loss - old_profit_or_loss
                stock_record.is_profit = profit_diff > 0
                stock_record.profit_or_loss = profit_diff

            stock_record.quantity += quantity
            stock_record.total_price += price_per_share * quantity
            stock_record.last_sell_date = last_sell_date
            stock_record.save()
        else:
            # Create a new SellStocks record if one doesn't exist
            SellStocks.objects.create(
                user=user,
                stock_id=stock_id,
                quantity=quantity,
                total_price=price_per_share * quantity,
                last_sell_date=last_sell_date,
                is_profit=is_profit,
                profit_or_loss=total_profit_or_loss
            )

    if request.method == 'POST':
        if 'add_stocks' in request.POST:
            add_stocks_to_portfolio()
        elif 'sell_stocks' in request.POST:
            sell_stocks_from_portfolio()

        return redirect(reverse("custom_portfolio"))

    # Get the success message from the session and clear it
    msg = request.session.pop('msg', "")

    # Prepare stock list (exclude stocks that have insufficient data)
    stocks = [stock for stock in Stock.objects.all() if len(FinancialStockData.objects.filter(stock=stock)) > 15]

    # Portfolio data preparation
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