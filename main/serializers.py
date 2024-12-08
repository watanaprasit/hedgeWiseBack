# serializers.py
from rest_framework import serializers
from .models import CurrencyData

class CurrencyDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = CurrencyData
        fields = ['currency_pair', 'open_price', 'high_price', 'low_price', 'close_price', 'volume', 'date']
