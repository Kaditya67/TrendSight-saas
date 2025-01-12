from datetime import datetime, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction

from user.models import User

from .models import (ComputedSectorData, ComputedStockData, FinancialStockData,
                     Sector, SectorFinancialData, Stock, Watchlist)


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
