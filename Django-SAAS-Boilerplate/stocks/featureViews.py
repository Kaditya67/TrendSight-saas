from datetime import datetime, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction

from user.models import User

from .models import (ComputedSectorData, ComputedStockData, FinancialStockData,
                     Portfolio, Sector, SectorFinancialData, SellStocks, Stock, Watchlist, userSetting)


@login_required
def watchlist(request):
    user = request.user
    user_watchlists = Watchlist.objects.filter(user=user)

    if request.method == 'POST':
        if 'update_stocks' in request.POST:
            updated_stocks = request.POST.getlist('stocks')
            # print(f"Updated stocks: {updated_stocks}")
            
            try:
                # Fetch the selected stocks by symbol
                selected_stocks = Stock.objects.filter(symbol__in=updated_stocks)
                
                # Use .set() to update the many-to-many relationship
                with transaction.atomic():
                    selected_watchlist = Watchlist.objects.filter(user=user, name="Watchlist").first()
                    if selected_watchlist:
                        selected_watchlist.stocks.set(selected_stocks)
                    return redirect('watchlist')
            except IntegrityError as e:
                print(f"An error occurred: {e}")
                messages.error(request, "An error occurred. Watchlist update failed.")
                return redirect('watchlist')

        elif 'update_sectors' in request.POST:
            # Get the list of checked sectors from the form
            checked_sectors = request.POST.getlist('sectors')
            # print(f"Checked sectors: {checked_sectors}")
            
            try:
                # Convert symbols to sector objects
                sectors_to_add = Sector.objects.filter(symbol__in=checked_sectors)
                
                # Use .set() to update the many-to-many relationship
                with transaction.atomic():
                    selected_watchlist = Watchlist.objects.filter(user=user, name="Watchlist").first()
                    if selected_watchlist:
                        selected_watchlist.sectors.set(sectors_to_add)
                    return redirect('watchlist')
            except IntegrityError as e:
                print(f"An error occurred: {e}")
                messages.error(request, "An error occurred. Watchlist update failed.")
                return redirect('watchlist')

        elif 'watchlist_name' in request.POST:
            watchlist_name = request.POST.get('watchlist_name')
            if watchlist_name:
                try:
                    last_watchlist = Watchlist.objects.order_by('-id').first()
                    next_id = last_watchlist.id + 1 if last_watchlist else 1

                    with transaction.atomic(): 
                        new_watchlist = Watchlist.objects.create(id=next_id, user=user, name=watchlist_name)
                        return redirect('watchlist', watchlist_id=new_watchlist.id)
                except IntegrityError as e:
                    print(f"An error occurred: {e}")
                    messages.error(request, "An error occurred. Watchlist creation failed.")
                    return redirect('watchlist') 

    if not user_watchlists.exists():
        return render(request, 'stocks/watchlist/watchlist.html', {
            "watchlists": [],
            "selected_watchlist": None,
            "watchlist_data": {}
        })

    watchlists = list(user_watchlists.values("id", "name", "count"))[1:]
    selected_watchlist = user_watchlists.first() 
    # print(f"Selected id is: {selected_watchlist.id}")
    stocks = []
    selected_stocks = [] 

    for stock in selected_watchlist.stocks.all():
        selected_stocks.append(stock)
        stock_data = {
            "id": stock.id,
            "symbol": stock.symbol,
            "name": stock.name,
            "chart":"charts",
            "dates": [],
            "data": []
        }

        stock_data_records = FinancialStockData.objects.filter(stock=stock).order_by('-date')[:30]
        stock_ema_records = ComputedStockData.objects.filter(stock=stock).order_by('-date')[:30]

        ema_counter = 0
        for (record, ema_record) in reversed(list(zip(stock_data_records, stock_ema_records))):
            stock_data["dates"].append(record.date.strftime('%d %b'))
            if record.close > ema_record.ema30:
                ema_counter = ema_counter + 1 if ema_counter >= 0 else 1
            else:
                ema_counter = ema_counter - 1 if ema_counter <= 0 else -1
            stock_data["data"].append(ema_counter)

        stock_data["dates"].reverse()  # Ensure chronological order
        stock_data["data"].reverse()
        stocks.append(stock_data)

    remaining_stocks = []
    for stock in Stock.objects.all():
        if stock not in selected_stocks:
            if len(FinancialStockData.objects.filter(stock=stock)) > 15:
                remaining_stocks.append(stock)

    selected_sectors = []
    for sector in selected_watchlist.sectors.all():
        selected_sectors.append(sector)
        sector_data = {
            "id": sector.id,
            "symbol": sector.symbol,
            "name": sector.name,
            "chart":"charts_sector",
            "dates": [],
            "data": []
        }

        sector_data_records = SectorFinancialData.objects.filter(sector=sector).order_by('-date')[:30]
        sector_ema_records = ComputedSectorData.objects.filter(sector=sector).order_by('-date')[:30]

        ema_counter = 0
        for (record, ema_record) in reversed(list(zip(sector_data_records, sector_ema_records))):
            sector_data["dates"].append(record.date.strftime('%d %b'))
            if record.close > ema_record.ema30:
                ema_counter = ema_counter + 1 if ema_counter >= 0 else 1
            else:
                ema_counter = ema_counter - 1 if ema_counter <= 0 else -1
            sector_data["data"].append(ema_counter)

        sector_data["dates"].reverse()  # Ensure chronological order
        sector_data["data"].reverse()
        stocks.append(sector_data)

    remaining_sectors = []
    for sector in Sector.objects.all():
        if sector not in selected_sectors:
            if len(SectorFinancialData.objects.filter(sector=sector)) > 15:
                remaining_sectors.append(sector)

    context = {
        "watchlists": watchlists,
        "selected_watchlist": selected_watchlist,
        "watchlist_data": stocks,
        "remaining_stocks": remaining_stocks,
        "remaining_sectors": remaining_sectors,
        "selected_stocks": selected_stocks,
        "selected_sectors": selected_sectors,
        'user_avatar': request.user.dp if request.user.dp else None
    }

    return render(request, 'stocks/watchlist/watchlist.html', context)



from django.contrib import messages
from django.db import IntegrityError, transaction
from django.shortcuts import redirect, render


def custom_watchlist(request, watchlist_id):
    user = request.user
    user_watchlists = Watchlist.objects.filter(user=user)

    if request.method == 'POST':
        if 'update_stocks' in request.POST:
            updated_stocks = request.POST.getlist('stocks')
            # print(f"Updated stocks: {updated_stocks}")
            
            try:
                # Fetch the selected stocks by symbol
                selected_stocks = Stock.objects.filter(symbol__in=updated_stocks)
                
                # Use .set() to update the many-to-many relationship
                with transaction.atomic():
                    selected_watchlist = Watchlist.objects.filter(id=watchlist_id).first()
                    # print(f"Selected watchlist: {selected_watchlist}")
                    if selected_watchlist:
                        selected_watchlist.stocks.set(selected_stocks)
                    return redirect('watchlist', watchlist_id=watchlist_id)
            except IntegrityError as e:
                print(f"An error occurred: {e}")
                messages.error(request, "An error occurred. Watchlist update failed.")
                return redirect('watchlist')

        elif 'update_sectors' in request.POST:
            # Get the list of checked sectors from the form
            checked_sectors = request.POST.getlist('sectors')
            # print(f"Checked sectors: {checked_sectors}")
            
            try:
                # Convert symbols to sector objects
                sectors_to_add = Sector.objects.filter(symbol__in=checked_sectors)
                
                # Use .set() to update the many-to-many relationship
                with transaction.atomic():
                    selected_watchlist = Watchlist.objects.filter(id=watchlist_id).first()
                    # print(f"Selected watchlist: {selected_watchlist}")
                    if selected_watchlist:
                        selected_watchlist.sectors.set(sectors_to_add)
                    return redirect('watchlist', watchlist_id=watchlist_id)
            except IntegrityError as e:
                print(f"An error occurred: {e}")
                messages.error(request, "An error occurred. Watchlist update failed.")
                return redirect('watchlist')
        elif 'watchlist_name' in request.POST:
            watchlist_name = request.POST.get('watchlist_name')
            if watchlist_name:
                try:
                    with transaction.atomic(): 
                        new_watchlist = Watchlist.objects.create(user=user, name=watchlist_name)
                        return redirect('watchlist', watchlist_id=new_watchlist.id)
                except IntegrityError as e:
                    print(f"An error occurred: {e}")
                    messages.error(request, "An error occurred. Watchlist creation failed.")
                    return redirect('watchlist')  # Or redirect to the appropriate page
        elif 'watchlist_name_rename' in request.POST:
            watchlist_name = request.POST.get('watchlist_name_rename')
            if watchlist_name:
                try:
                    with transaction.atomic(): 
                        Watchlist.objects.filter(id=watchlist_id).update(name=watchlist_name)
                        return redirect('watchlist', watchlist_id=watchlist_id)
                except IntegrityError as e:
                    print(f"An error occurred: {e}")
                    messages.error(request, "An error occurred. Watchlist update failed.")
        elif 'delete_watchlist' in request.POST:
            Watchlist.objects.filter(id=watchlist_id).delete()
            return redirect('watchlist')

    if not user_watchlists.exists():
        return render(request, 'stocks/watchlist/watchlist.html', {
            "watchlists": [],
            "selected_watchlist": None,
            "watchlist_data": {}
        })

    watchlists = list(user_watchlists.values("id", "name", "count"))
    default_watchlist = watchlists[0]
    watchlists = watchlists[1:] 

    selected_watchlist = user_watchlists.filter(id=watchlist_id).first()
    # print(f"Selected id is: {selected_watchlist.id}")
    stocks = [] 
    selected_stocks = [] 
    # Gathering stock data for the selected watchlist
    for stock in selected_watchlist.stocks.all():
        selected_stocks.append(stock)
        stock_data = {
            "id": stock.id,
            "symbol": stock.symbol,
            "name": stock.name,
            "chart":"charts",
            "dates": [],
            "data": []
        }

        stock_data_records = FinancialStockData.objects.filter(stock=stock).order_by('-date')[:30]
        stock_ema_records = ComputedStockData.objects.filter(stock=stock).order_by('-date')[:30]

        ema_counter = 0
        for (record, ema_record) in reversed(list(zip(stock_data_records, stock_ema_records))):
            stock_data["dates"].append(record.date.strftime('%d %b'))
            if record.close > ema_record.ema30:
                ema_counter = ema_counter + 1 if ema_counter >= 0 else 1
            else:
                ema_counter = ema_counter - 1 if ema_counter <= 0 else -1
            stock_data["data"].append(ema_counter)

        stock_data["dates"].reverse()  # Ensure chronological order
        stock_data["data"].reverse()
        stocks.append(stock_data)

    remaining_stocks = []
    for stock in Stock.objects.all():
        if stock not in selected_stocks:
            if len(FinancialStockData.objects.filter(stock=stock)) > 15:
                remaining_stocks.append(stock)

    # Gathering sector data for the selected watchlist
    selected_sectors = []
    for sector in selected_watchlist.sectors.all():
        selected_sectors.append(sector)
        sector_data = {
            "id": sector.id,
            "symbol": sector.symbol,
            "name": sector.name,
            "chart":"charts_sector",
            "dates": [],
            "data": []
        }

        sector_data_records = SectorFinancialData.objects.filter(sector=sector).order_by('-date')[:30]
        sector_ema_records = ComputedSectorData.objects.filter(sector=sector).order_by('-date')[:30]

        ema_counter = 0
        for (record, ema_record) in reversed(list(zip(sector_data_records, sector_ema_records))):
            sector_data["dates"].append(record.date.strftime('%d %b'))
            if record.close > ema_record.ema30:
                ema_counter = ema_counter + 1 if ema_counter >= 0 else 1
            else:
                ema_counter = ema_counter - 1 if ema_counter <= 0 else -1
            sector_data["data"].append(ema_counter)

        sector_data["dates"].reverse()  # Ensure chronological order
        sector_data["data"].reverse()
        stocks.append(sector_data)

    remaining_sectors = []
    for sector in Sector.objects.all():
        if sector not in selected_sectors:
            if len(SectorFinancialData.objects.filter(sector=sector)) > 15:
                remaining_sectors.append(sector)
    # print(f"Remaining sectors: {remaining_sectors}")

    context = {
        "default_watchlist": default_watchlist,
        "watchlists": watchlists,
        "selected_watchlist": selected_watchlist,
        "watchlist_data": stocks,
        "watchlist_id": watchlist_id,
        "remaining_stocks": remaining_stocks,
        "remaining_sectors": remaining_sectors,
        "selected_stocks": selected_stocks,
        "selected_sectors": selected_sectors,
        'user_avatar': request.user.dp if request.user.dp else None
    }
    # print(context)

    return render(request, 'stocks/watchlist/custom_watchlist.html', context)

from django.shortcuts import render, redirect
from .models import Sector, Watchlist, SectorFinancialData, ComputedSectorData

@login_required
def sectors(request):
    # Get all sector records
    sector_records = Sector.objects.all()
    sectors = []
    user = request.user 

    # Fetch the watchlists associated with the user, ordered by count (descending)
    watchlists = Watchlist.objects.filter(user=user).order_by('-count')
    # print(f"Watchlists: {watchlists}")
    if request.method == 'POST':
        # print("POST : ", request.POST)
        # Handle the POST request to add sector to watchlist
        if 'add_to_watchlist' in request.POST:
            # Get the sector_id and watchlist_name from the POST data
            sector_id = request.POST.get('sector_id')
            watchlist_id = request.POST.get('watchlist_name')

            # Fetch the sector and watchlist from the database
            try:
                sector = Sector.objects.get(id=sector_id)
                watchlist = Watchlist.objects.get(id=watchlist_id, user=user)
                
                if sector in watchlist.sectors.all():
                    # If the sector is already in the watchlist, do nothing
                    messages.error(request, "Sector is already in the watchlist.")
                    return redirect('sector')  # Replace 'sectors' with the name of your view
                # Add the sector to the watchlist (you may want to adjust the logic here)
                watchlist.sectors.add(sector)  # Assuming you have a ManyToMany field in Watchlist for sectors
                watchlist.count += 1  # Increment the count of sectors in the watchlist
                watchlist.save()
                messages.success(request, "Sector added to watchlist successfully.")

                # Optionally, you could redirect to avoid re-submitting the form
                return redirect('sector')  # Replace 'sectors' with the name of your view
            except Sector.DoesNotExist:
                print(f"Sector with id {sector_id} not found.")
            except Watchlist.DoesNotExist:
                print(f"Watchlist with id {watchlist_id} not found.")

    # For each sector, gather the financial data and computed sector data
    for sector in sector_records:
        data_records = SectorFinancialData.objects.filter(sector=sector).order_by('-date')[:30]
        if len(data_records) < 30:
            continue  # Skip sectors with insufficient data

        ema_records = ComputedSectorData.objects.filter(sector=sector).order_by('-date')[:30]
        if len(ema_records) < 30:
            continue  # Skip sectors with insufficient EMA data

        sector_data = {
            "id": sector.id,
            "symbol": sector.symbol,
            "name": sector.name,
            "dates": [],
            "data": []
        }

        ema_counter = 0
        for record, ema_record in reversed(list(zip(data_records, ema_records))):
            sector_data["dates"].append(record.date.strftime('%d %b'))
            if record.close > ema_record.ema30:
                ema_counter = ema_counter + 1 if ema_counter >= 0 else 1
            else:
                ema_counter = ema_counter - 1 if ema_counter <= 0 else -1
            sector_data["data"].append(ema_counter)

        sector_data["dates"].reverse()  # Ensure chronological order
        sector_data["data"].reverse()
        sectors.append(sector_data)

    context = {
        'sectors': sectors,
        'watchlists': watchlists,
        'user_avatar': request.user.dp if request.user.dp else None
    }
    return render(request, 'stocks/Table/sector_table.html', context)

@login_required
def stock(request):
    stock_records = Stock.objects.all()  # Get all stocks, not just the first
    stocks = []
    user = request.user 
    watchlists = Watchlist.objects.filter(user=user).order_by('-count')

    if request.method == 'POST':
        if 'add_to_watchlist' in request.POST:
                # Get the sector_id and watchlist_name from the POST data
                stock_id = request.POST.get('stock_id')
                watchlist_id = request.POST.get('watchlist_name')

                # Fetch the sector and watchlist from the database
                try:
                    stock = Stock.objects.get(id=stock_id)
                    watchlist = Watchlist.objects.get(id=watchlist_id, user=user)
                    
                    if stock in watchlist.stocks.all():
                        # If the sector is already in the watchlist, do nothing
                        messages.error(request, "Stock is already in the watchlist.")
                        return redirect('stock')  # Replace 'sectors' with the name of your view
                    # Add the sector to the watchlist (you may want to adjust the logic here)
                    watchlist.stocks.add(stock)  # Assuming you have a ManyToMany field in Watchlist for sectors
                    watchlist.count += 1  # Increment the count of sectors in the watchlist
                    watchlist.save()
                    messages.success(request, "Stock added to watchlist successfully.")

                    # Optionally, you could redirect to avoid re-submitting the form
                    return redirect('stock')  # Replace 'sectors' with the name of your view
                except Stock.DoesNotExist:
                    print(f"Stock with id {stock_id} not found.")
                except Watchlist.DoesNotExist:
                    print(f"Watchlist with id {watchlist_id} not found.")
                    
    for stock in stock_records:
      
        data_records = FinancialStockData.objects.filter(stock=stock).order_by('-date')[:30]
        if len(data_records) < 30:
            continue 

        ema_records = ComputedStockData.objects.filter(stock=stock).order_by('-date')[:30]
        if len(ema_records) < 30:
            continue

          
        stock_data = {
            "id": stock.id,
            "symbol": stock.symbol,
            "name": stock.name,
            "dates": [],
            "data": []
        }

        ema_counter = 0
        for (record, ema_record) in reversed(list(zip(data_records, ema_records))):
            stock_data["dates"].append(record.date.strftime('%d %b'))
            if record.close > ema_record.ema30:
                ema_counter = ema_counter + 1 if ema_counter >= 0 else 1
            else:
                ema_counter = ema_counter - 1 if ema_counter <= 0 else -1
            stock_data["data"].append(ema_counter)

        stock_data["dates"].reverse()  # Ensure chronological order
        stock_data["data"].reverse()
        stocks.append(stock_data)
    
    context = {
        'stocks': stocks,
        'watchlists': watchlists,
        'user_avatar': request.user.dp if request.user.dp else None
    }
    # print(context)
    return render(request, 'stocks/Table/stock_table.html', context)

from decimal import Decimal

from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse


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
        print(request.POST)
        if 'add_stocks' in request.POST:
            add_stocks_to_portfolio()
        elif 'sell_stocks' in request.POST:
            sell_stocks_from_portfolio()
        elif 'delete_record' in request.POST:
            record_type = request.POST.get('record_type')
            stock_id  = request.POST.get('stock_id')
            if record_type == 'portfolio':
                Portfolio.objects.filter(user=user, stock_id=stock_id).delete()
            elif record_type == 'sell':
                SellStocks.objects.filter(user=user, stock_id=stock_id).delete()

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
        "total_invested_capital": total_invested_capital,
        'user_avatar': request.user.dp if request.user.dp else None
    }

    return render(request, 'stocks/portfolio/custom_portfolio.html', context)
 
from django.shortcuts import render
from .models import FinancialStockData, ComputedStockData

def charts(request):
    # Retrieve stock symbol from query parameters or default to a placeholder
    symbol = request.GET.get('symbol', 'TATAMOTORS.NS')
    stock_symbols = Stock.objects.all()
    sector_symbols = Sector.objects.all()

    # Function to fetch stock data and moving average data
    def get_stock_data(symbol, num_days):
        stock_data = FinancialStockData.objects.filter(stock__symbol=symbol).order_by('-date')[:num_days]
        dates = [stock.date.strftime('%Y-%m-%d') for stock in stock_data]
        stock_prices = [round(stock.close, 2) for stock in stock_data]

        moving_avg50_data = ComputedStockData.objects.filter(stock__symbol=symbol).order_by('-date').values_list('ema50')[:num_days]
        moving_avg50 = [round(data[0],2) for data in moving_avg50_data]

        return dates, stock_prices, moving_avg50

    # Check if the request method is POST
    if request.method == 'POST': 
        range_data = request.POST.get('range', 'day')

        # Set the number of days based on the selected range
        if range_data == 'week':
            num_days = 5
        elif range_data == 'year':
            num_days = 365
        else:
            num_days = 30   
             
        dates, stock_prices, moving_avg50 = get_stock_data(symbol, num_days)

        context = {
            'dates': dates,
            'stock_prices': stock_prices,
            'moving_avg50': moving_avg50,
            'symbol': symbol,
            'stock_symbols':stock_symbols,
            'sector_symbols':sector_symbols,
            'user_avatar': request.user.dp if request.user.dp else None 
        }

        return render(request, 'stocks/charts/charts.html', context)
 
    dates, stock_prices, moving_avg50 = get_stock_data(symbol, 30)

    context = {
        'dates': dates,
        'stock_prices': stock_prices,
        'moving_avg50': moving_avg50,
        'symbol': symbol, 
        'stock_symbols':stock_symbols,
        'sector_symbols':sector_symbols,
        'user_avatar': request.user.dp if request.user.dp else None
    }

    return render(request, 'stocks/charts/charts.html', context)

from django.shortcuts import render, get_object_or_404
from .models import Stock, FinancialStockData, ComputedStockData, userSetting, Sector

def stock_chart(request, stock_id):
    user = request.user
    # Get user's selected EMA, falling back to default if not set
    selected_ema = userSetting.objects.filter(user=user).first().defaultEma if userSetting.objects.filter(user=user).exists() else 10
    print(selected_ema)
    
    # Retrieve all stock symbols and sector symbols for dropdowns
    stock_symbols_all = Stock.objects.all() 
    stock_symbols = []
    valid_stock=""
    for stock in stock_symbols_all:
        if len(FinancialStockData.objects.filter(stock=stock)) > 15:
            valid_stock = stock
            stock_symbols.append(stock)
    selected_range = 'year'

    # Retrieve stock symbol from the Stock model
    try:
        stock = get_object_or_404(Stock, id=stock_id)
        if(len(FinancialStockData.objects.filter(stock=stock)) < 15):
            stock = valid_stock
    except Http404:
        stock = Sector(symbol="TATAMOTORS.NS")

    # Retrieve stock symbol from the Stock model
    symbol = stock.symbol

    # EMA options (you can dynamically fetch this based on your use case)
    emas = [10, 20, 50, 100, 200]

    # Function to fetch stock data and moving average data
    def get_stock_data(symbol, num_days):
        stock_data = FinancialStockData.objects.filter(stock__symbol=symbol).order_by('-date')[:num_days]
        dates = [stock.date.strftime('%Y-%m-%d') for stock in stock_data]
        stock_prices = [round(stock.close, 2) for stock in stock_data]

        # Fetch moving average data for the selected EMA (you might want to adapt this to use dynamic EMA)
        moving_avg_data = ComputedStockData.objects.filter(stock__symbol=symbol).order_by('-date').values_list(f'ema{selected_ema}')[:num_days]
        moving_avg = [round(data[0], 2) for data in moving_avg_data]

        return dates, stock_prices, moving_avg

    # Handle POST request (when user selects range or makes other changes)
    if request.method == 'POST':
        range_data = request.POST.get('range', 'day')

        # Set the number of days based on the selected range
        if range_data == 'week':
            selected_range = 'week'
            num_days = 5
        elif range_data == 'month':
            selected_range = 'month'
            num_days = 30
        else:
            selected_range = 'year'
            num_days = 365  # Default to 30 days
            
        dates, stock_prices, moving_avg = get_stock_data(symbol, num_days)

        context = {
            'dates': dates,
            'stock_prices': stock_prices,
            'moving_avg': moving_avg,
            'symbol': symbol,
            'stock_symbols': stock_symbols, 
            'stock_id': stock_id,
            'emas': emas,
            'selected_ema': selected_ema,
            'selected_range' : selected_range,
            'user_avatar': request.user.dp if request.user.dp else None
        }

        return render(request, 'stocks/charts/stock_charts.html', context)

    # For initial load (GET request)
    dates, stock_prices, moving_avg = get_stock_data(symbol, 365)

    context = {
        'dates': dates,
        'stock_prices': stock_prices,
        'moving_avg': moving_avg,
        'symbol': symbol,
        'stock_symbols': stock_symbols, 
        'stock_id': stock_id,
        'emas': emas,
        'selected_ema': selected_ema,
        'selected_range' : selected_range,
        'user_avatar': request.user.dp if request.user.dp else None
    }

    return render(request, 'stocks/charts/stock_charts.html', context)

from django.http import Http404

def sector_chart(request, sector_id):
    user = request.user
    # Get user's selected EMA, falling back to default if not set
    selected_ema = userSetting.objects.filter(user=user).first().defaultEma if userSetting.objects.filter(user=user).exists() else 10
    print(selected_ema)
    
      
    # Retrieve all stock symbols and sector symbols for dropdowns
    sector_symbols_all = Sector.objects.all() 
    sector_symbols = []
    valid_sector=""
    for sector in sector_symbols_all:
        if len(SectorFinancialData.objects.filter(sector=sector)) > 15:
            valid_sector = sector
            sector_symbols.append(sector)
    selected_range = 'year'

    # Retrieve stock symbol from the Stock model
    try:
        sector = get_object_or_404(Sector, id=sector_id)
        if(len(SectorFinancialData.objects.filter(sector=sector)) < 15):
            sector = valid_sector
    except Http404:
        sector = Sector(symbol="^NSEI")

    symbol = sector.symbol
    
    # EMA options (you can dynamically fetch this based on your use case)
    emas = [10, 20, 50, 100, 200]

    # Function to fetch stock data and moving average data
    def get_sector_data(symbol, num_days):
        sector_data = SectorFinancialData.objects.filter(sector__symbol=symbol).order_by('-date')[:num_days]
        dates = [sector.date.strftime('%Y-%m-%d') for sector in sector_data]
        sector_prices = [round(sector.close, 2) for sector in sector_data]

        # Fetch moving average data for the selected EMA (you might want to adapt this to use dynamic EMA)
        moving_avg_data = ComputedSectorData.objects.filter(sector__symbol=symbol).order_by('-date').values_list(f'ema{selected_ema}')[:num_days]
        moving_avg = [round(data[0], 2) for data in moving_avg_data]

        return dates, sector_prices, moving_avg

    # Handle POST request (when user selects range or makes other changes)
    if request.method == 'POST':
        range_data = request.POST.get('range', 'day')

        # Set the number of days based on the selected range
        if range_data == 'week':
            selected_range = 'week'
            num_days = 5
        elif range_data == 'month':
            selected_range = 'month'
            num_days = 30
        else:
            selected_range = 'year'
            num_days = 365  # Default to 30 days
            
        dates, sector_prices, moving_avg = get_sector_data(symbol, num_days)

        context = {
            'dates': dates,
            'stock_prices': sector_prices,
            'moving_avg': moving_avg,
            'symbol': symbol, 
            'sector_symbols': sector_symbols,
            'sector_id': sector_id,
            'emas': emas,
            'selected_ema': selected_ema,
            'selected_range' : selected_range,
            'user_avatar': request.user.dp if request.user.dp else None
        }

        return render(request, 'stocks/charts/sector_charts.html', context)

    # For initial load (GET request)
    dates, sector_prices, moving_avg = get_sector_data(symbol, 365)

    context = {
        'dates': dates,
        'stock_prices': sector_prices,
        'moving_avg': moving_avg,
        'symbol': symbol, 
        'sector_symbols': sector_symbols,
        'sector_id': sector_id,
        'emas': emas,
        'selected_ema': selected_ema,
        'selected_range' : selected_range,
        'user_avatar': request.user.dp if request.user.dp else None
    }

    return render(request, 'stocks/charts/sector_charts.html', context)

from django.http import JsonResponse

@login_required
def change_ema(request):
    user = request.user
    if request.method == "POST":
        # print(request.POST)  # Debugging the POST data
        if 'ema' in request.POST:
            selected_ema = request.POST.get('ema')
            # Try to get or create the userSetting object
            user_setting, created = userSetting.objects.update_or_create(
                user=user,
                defaults={'defaultEma': int(selected_ema)}
            )
            
            if created:
                message = "EMA setting created successfully."
            else:
                message = "EMA updated successfully."
            
            return JsonResponse({"message": message})
    
    return JsonResponse({"message": "Error processing request."})