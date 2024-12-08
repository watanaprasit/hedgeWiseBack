from django.shortcuts import render
from datetime import timedelta
from django.utils import timezone
from .models import CurrencyData
from itertools import groupby
from decimal import Decimal, ROUND_DOWN
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import CurrencyDataSerializer  # Import the serializer

# View for the homepage to display the historical data for all currency pairs
def home(request):
    # Get the past 30 days of data for all currency pairs
    end_time = timezone.now()
    start_time = end_time - timedelta(days=30)  # Get data for the last 30 days

    # Retrieve data for all currency pairs from the CurrencyData model
    currency_data = CurrencyData.objects.filter(
        date__gte=start_time,
        date__lte=end_time
    ).order_by('currency_pair', 'date')  # Order by currency pair and date

    # Group the data by currency pair
    grouped_data = {}
    for key, group in groupby(currency_data, lambda x: x.currency_pair):
        grouped_data[key] = list(group)

    # Round decimal fields to 3 places for each entry in grouped_data
    for currency_pair, entries in grouped_data.items():
        for entry in entries:
            entry.open_price = Decimal(entry.open_price).quantize(Decimal('0.001'), rounding=ROUND_DOWN)
            entry.high_price = Decimal(entry.high_price).quantize(Decimal('0.001'), rounding=ROUND_DOWN)
            entry.low_price = Decimal(entry.low_price).quantize(Decimal('0.001'), rounding=ROUND_DOWN)
            entry.close_price = Decimal(entry.close_price).quantize(Decimal('0.001'), rounding=ROUND_DOWN)
            entry.volume = Decimal(entry.volume).quantize(Decimal('0.001'), rounding=ROUND_DOWN)

    # Prepare the data to be passed to the template
    context = {
        "grouped_data": grouped_data
    }

    return render(request, 'home.html', context)


# API endpoint to return all currency data as JSON
@api_view(['GET'])
def get_currency_data(request):
    # Get the past 30 days of data for all currency pairs
    end_time = timezone.now()
    start_time = end_time - timedelta(days=30)  # Get data for the last 30 days

    # Retrieve data for all currency pairs from the CurrencyData model
    currency_data = CurrencyData.objects.filter(
        date__gte=start_time,
        date__lte=end_time
    ).order_by('currency_pair', 'date')  # Order by currency pair and date

    # Serialize the data using the CurrencyDataSerializer
    serializer = CurrencyDataSerializer(currency_data, many=True)

    # Return the serialized data as JSON response
    return Response(serializer.data)










