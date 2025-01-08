from django import forms
from django.contrib import admin
from django.db import models
from import_export.admin import ImportExportModelAdmin
from unfold.admin import ModelAdmin
from unfold.contrib.import_export.forms import ExportForm, ImportForm

from .models import (ComputedSectorData, ComputedStockData, FinancialStockData,
                     PrevVolumes, Sector, SectorFinancialData, Stock)


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

# Registering the models and their custom admins
admin.site.register(Stock, StockAdmin)
admin.site.register(FinancialStockData, FinancialStockDataAdmin)
admin.site.register(PrevVolumes, PrevVolumesAdmin)
admin.site.register(ComputedStockData, ComputedStockDataAdmin)
admin.site.register(Sector, SectorAdmin)  
admin.site.register(SectorFinancialData, SectorFinancialDataAdmin)
admin.site.register(ComputedSectorData, ComputedSectorDataAdmin)
