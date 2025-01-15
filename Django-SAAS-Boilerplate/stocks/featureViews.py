from datetime import datetime, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction

from user.models import User

from .models import (ComputedSectorData, ComputedStockData, FinancialStockData,
                     Portfolio, Sector, SectorFinancialData, SellStocks, Stock,
                     User, Watchlist)


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
            "symbol": stock.symbol,
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
            "symbol": sector.symbol,
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
        "selected_sectors": selected_sectors
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
            "symbol": stock.symbol,
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
            "symbol": sector.symbol,
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
        "selected_sectors": selected_sectors
    }
    # print(context)

    return render(request, 'stocks/watchlist/custom_watchlist.html', context)

from django.shortcuts import render, redirect
from .models import Sector, Watchlist, SectorFinancialData, ComputedSectorData

def sectors(request):
    # Get all sector records
    sector_records = Sector.objects.all()
    sectors = []
    user = request.user 

    # Fetch the watchlists associated with the user, ordered by count (descending)
    watchlists = Watchlist.objects.filter(user=user).order_by('-count')
    print(f"Watchlists: {watchlists}")
    if request.method == 'POST':
        print("POST : ", request.POST)
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
                    return redirect('sectors')  # Replace 'sectors' with the name of your view
                # Add the sector to the watchlist (you may want to adjust the logic here)
                watchlist.sectors.add(sector)  # Assuming you have a ManyToMany field in Watchlist for sectors
                watchlist.count += 1  # Increment the count of sectors in the watchlist
                watchlist.save()
                messages.success(request, "Sector added to watchlist successfully.")

                # Optionally, you could redirect to avoid re-submitting the form
                return redirect('sectors')  # Replace 'sectors' with the name of your view
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
        'watchlists': watchlists
    }
    return render(request, 'stocks/Table/sector_table.html', context)

def stock(request):
    stock_records = Stock.objects.all()  # Get all stocks, not just the first
    stocks = []
    user = request.user 
    watchlists = Watchlist.objects.filter(user=user).order_by('-count')
    for stock in stock_records:
      
        data_records = FinancialStockData.objects.filter(stock=stock).order_by('-date')[:30]
        if len(data_records) < 30:
            continue 

        ema_records = ComputedStockData.objects.filter(stock=stock).order_by('-date')[:30]
        if len(ema_records) < 30:
            continue

          
        stock_data = {
            "symbol": stock.symbol,
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
        'stocks': stocks
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
        "total_invested_capital": total_invested_capital
    }

    return render(request, 'stocks/portfolio/custom_portfolio.html', context)