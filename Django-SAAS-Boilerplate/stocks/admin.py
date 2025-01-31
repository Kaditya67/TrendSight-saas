from django import forms
from django.contrib import admin
from django.db import models
from import_export.admin import ImportExportModelAdmin
from unfold.admin import ModelAdmin
from unfold.contrib.import_export.forms import ExportForm, ImportForm

from .models import (ComputedSectorData, ComputedStockData, FinancialStockData, sectorIndicatorCount,
                     PrevVolumes, Sector, SectorFinancialData, Stock, userSetting)
from .models import Watchlist,Portfolio, SellStocks

# Stock Models Administration
class StockAdmin(ModelAdmin, ImportExportModelAdmin):
    import_form_class = ImportForm
    export_form_class = ExportForm
    list_display = ('id', 'symbol', 'name', 'get_sectors', 'last_updated')
    search_fields = ('symbol', 'name')

    fieldsets = (
        (None, {
            'fields': ('name', 'symbol', 'sectors')
        }),
    )
    autocomplete_fields = ['sectors']

    # formfield_overrides = {
    # models.ManyToManyField: {'widget': forms.CheckboxSelectMultiple},
    # }

    def get_sectors(self, obj):
        return ", ".join([sector.name for sector in obj.sectors.all()])
    get_sectors.short_description = 'Sectors'


class FinancialStockDataAdmin(ModelAdmin):
    list_display = ('stock','date','high', 'low', 'close', 'open', 'volume', 'last_updated')
    list_filter = ('last_updated',)
    search_fields = ('stock__symbol',)

class PrevVolumesAdmin(ModelAdmin):
    list_display = ('stock','date','volume20', 'volume50') 

class ComputedStockDataAdmin(ModelAdmin):
    list_display = ('stock','date','rs', 'rsi', 'ema10', 'ema20', 'ema30', 'ema50', 'ema100', 'ema200', 'volume20', 'volume50', 'last_updated')
    list_filter = ('last_updated',)
    search_fields = ('stock__symbol',)

# Sector Models Administration
class SectorAdmin(ModelAdmin,ImportExportModelAdmin):
    import_form_class = ImportForm
    export_form_class = ExportForm
    list_display = ('id', 'name','symbol','description', 'last_updated')
    search_fields = ('name',)

class SectorFinancialDataAdmin(ModelAdmin):
    list_display = ('sector', 'high', 'low', 'close', 'open', 'date','last_updated')
    list_filter = ('last_updated',)
    search_fields = ('sector__name',)

class ComputedSectorDataAdmin(ModelAdmin):
    list_display = ('sector', 'rs', 'rsi', 'ema10', 'ema20', 'ema30', 'ema50', 'ema100', 'ema200','date', 'last_updated')
    list_filter = ('last_updated',)
    search_fields = ('sector__name',)

class WatchlistAdmin(ModelAdmin):
    list_display = ('id','name', 'user', 'get_stocks', 'get_sectors','count', 'last_updated')
    search_fields = ('user__username',)
    autocomplete_fields = ['stocks', 'sectors']

    def get_stocks(self, obj):
        return ", ".join(stock.symbol for stock in obj.stocks.all())
    get_stocks.short_description = 'Stocks'

    def get_sectors(self, obj):
        return ", ".join(sector.name for sector in obj.sectors.all())
    get_sectors.short_description = 'Sectors'

class PortfolioAdmin(ModelAdmin):
    list_display = ('id', 'user', 'get_stock', 'last_purchased_date', 'quantity', 'average_purchase_price')
    search_fields = ('user__name',) 

    def get_stock(self, obj):
        return obj.stock.name
    get_stock.short_description = 'Stock'


class SellStocksAdmin(ModelAdmin):
    list_display = ('id', 'user', 'get_stock', 'total_price', 'quantity', 'last_sell_date', 'is_profit', 'profit_or_loss')
    search_fields = ('user__name',) 

    def get_stock(self, obj):
        return obj.stock.name
    get_stock.short_description = 'Stock'

class sectorIndicatorCountAdmin(ModelAdmin):
    list_display = ('sector', 'date', 'ema10Count', 'ema20Count', 'ema30Count', 'ema50Count', 'ema100Count', 'ema200Count', 'last_updated')
    search_fields = ('sector__name','sector__symbol')
    
class userSettingAdmin(ModelAdmin):
    list_display = ('user','defaultEma')

# Registering the models and their custom admins
admin.site.register(Stock, StockAdmin)
admin.site.register(FinancialStockData, FinancialStockDataAdmin)
admin.site.register(PrevVolumes, PrevVolumesAdmin)
admin.site.register(ComputedStockData, ComputedStockDataAdmin)
admin.site.register(Sector, SectorAdmin)  
admin.site.register(SectorFinancialData, SectorFinancialDataAdmin)
admin.site.register(ComputedSectorData, ComputedSectorDataAdmin)
admin.site.register(Watchlist, WatchlistAdmin)
admin.site.register(Portfolio, PortfolioAdmin)
admin.site.register(SellStocks, SellStocksAdmin)
admin.site.register(sectorIndicatorCount, sectorIndicatorCountAdmin)
admin.site.register(userSetting, userSettingAdmin)