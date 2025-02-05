from decimal import Decimal, ROUND_DOWN
from django.db import models

class CurrencyData(models.Model):
    currency_pair = models.CharField(max_length=10)
    open_price = models.DecimalField(max_digits=12, decimal_places=5)
    high_price = models.DecimalField(max_digits=12, decimal_places=5)
    low_price = models.DecimalField(max_digits=12, decimal_places=5)
    close_price = models.DecimalField(max_digits=12, decimal_places=5)
    volume = models.DecimalField(max_digits=15, decimal_places=5)
    date = models.DateTimeField()

    def save(self, *args, **kwargs):
        self.open_price = Decimal(self.open_price).quantize(Decimal('0.001'), rounding=ROUND_DOWN)
        self.high_price = Decimal(self.high_price).quantize(Decimal('0.001'), rounding=ROUND_DOWN)
        self.low_price = Decimal(self.low_price).quantize(Decimal('0.001'), rounding=ROUND_DOWN)
        self.close_price = Decimal(self.close_price).quantize(Decimal('0.001'), rounding=ROUND_DOWN)
        self.volume = Decimal(self.volume).quantize(Decimal('0.001'), rounding=ROUND_DOWN)

        super().save(*args, **kwargs) 

    def __str__(self):
        return f'{self.currency_pair} - {self.date}'
    
class BrentCrudeData(models.Model):
    date = models.DateTimeField()
    price = models.DecimalField(max_digits=12, decimal_places=3)

    def __str__(self):
        return f'Brent Crude Index - {self.date}'

class GeopoliticalNews(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    url = models.URLField()
    published_at = models.DateTimeField()
    source = models.CharField(max_length=100)
    
    def __str__(self):
        return self.title
