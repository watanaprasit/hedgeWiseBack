# main/admin.py
from django.contrib import admin
from .models import CurrencyData

class CurrencyDataAdmin(admin.ModelAdmin):
    list_display = ('currency_pair', 'date', 'open_price', 'high_price', 'low_price', 'close_price', 'volume')
    search_fields = ('currency_pair',)

# Register the model with the custom admin view
admin.site.register(CurrencyData, CurrencyDataAdmin)
