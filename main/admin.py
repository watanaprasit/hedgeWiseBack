from django.contrib import admin
from .models import CurrencyData, BrentCrudeData, GeopoliticalNews

class CurrencyDataAdmin(admin.ModelAdmin):
    list_display = ('currency_pair', 'date', 'open_price', 'high_price', 'low_price', 'close_price', 'volume')
    search_fields = ('currency_pair',)

class BrentCrudeDataAdmin(admin.ModelAdmin):
    list_display = ('date', 'price')
    search_fields = ('date',)

class GeopoliticalNewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'published_at', 'short_description', 'source')
    search_fields = ('title',)

    def short_description(self, obj):
        return obj.description[:50]  # Truncate description to the first 50 characters
    short_description.short_description = 'Description'


# Register models with custom admin views
admin.site.register(CurrencyData, CurrencyDataAdmin)
admin.site.register(BrentCrudeData, BrentCrudeDataAdmin)
admin.site.register(GeopoliticalNews, GeopoliticalNewsAdmin)

