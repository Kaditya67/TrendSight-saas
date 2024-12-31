from django.contrib import admin
from .models import Stock, FinancialStockData, ComputedStockData, Sector, SectorStock, SectorFinancialData, ComputedSectorData
from unfold.admin import ModelAdmin

# Stock Models Administration
class StockAdmin(ModelAdmin):
    list_display = ('id', 'symbol', 'name', 'last_updated')
    search_fields = ('symbol', 'name')

class FinancialStockDataAdmin(ModelAdmin):
    list_display = ('stock', 'high', 'low', 'close', 'open', 'volume', 'last_updated')
    list_filter = ('last_updated',)
    search_fields = ('stock__symbol',)

class ComputedStockDataAdmin(ModelAdmin):
    list_display = ('stock', 'rs', 'rsi', 'ema10', 'ema20', 'ema30', 'ema50', 'ema100', 'ema200', 'volume20', 'volume50', 'last_updated')
    list_filter = ('last_updated',)
    search_fields = ('stock__symbol',)

# Sector Models Administration
class SectorAdmin(ModelAdmin):
    list_display = ('id', 'name','symbol','description', 'last_updated')
    search_fields = ('name',)

class SectorStockAdmin(ModelAdmin):
    list_display = ('sector', 'stock', 'last_updated')
    list_filter = ('last_updated',)

class SectorFinancialDataAdmin(ModelAdmin):
    list_display = ('sector', 'avg_high', 'avg_low', 'avg_close', 'avg_open', 'total_volume', 'last_updated')
    list_filter = ('last_updated',)
    search_fields = ('sector__name',)

class ComputedSectorDataAdmin(ModelAdmin):
    list_display = ('sector', 'avg_rs', 'avg_rsi', 'avg_ema10', 'avg_ema20', 'avg_ema30', 'avg_ema50', 'avg_ema100', 'avg_ema200', 'volume_trend', 'last_updated')
    list_filter = ('last_updated',)
    search_fields = ('sector__name',)

# Registering the models and their custom admins
admin.site.register(Stock, StockAdmin)
admin.site.register(FinancialStockData, FinancialStockDataAdmin)
admin.site.register(ComputedStockData, ComputedStockDataAdmin)
admin.site.register(Sector, SectorAdmin)
admin.site.register(SectorStock, SectorStockAdmin)
admin.site.register(SectorFinancialData, SectorFinancialDataAdmin)
admin.site.register(ComputedSectorData, ComputedSectorDataAdmin)
