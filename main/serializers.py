# serializers.py
from rest_framework import serializers
from .models import CurrencyData, BrentCrudeData

class CurrencyDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = CurrencyData
        fields = ['currency_pair', 'open_price', 'high_price', 'low_price', 'close_price', 'volume', 'date']


class BrentCrudeDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = BrentCrudeData
        fields = ['date', 'price']
