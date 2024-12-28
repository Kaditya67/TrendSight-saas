from django.contrib import admin

# Register your models here.

from .models import FStockData, CStockData

admin.site.register(FStockData)
admin.site.register(CStockData)
