from django.shortcuts import render
from datetime import timedelta
from django.utils import timezone
from .models import CurrencyData, BrentCrudeData, GeopoliticalNews
from itertools import groupby
from decimal import Decimal, ROUND_DOWN
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import CurrencyDataSerializer, BrentCrudeDataSerializer, GeopoliticalNewsSerializer
from django.db.models import Q

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

@api_view(['GET'])
def get_brent_crude_data(request):
    # Get the past 30 days of data for Brent Crude Index
    end_time = timezone.now()
    start_time = end_time - timedelta(days=30)

    # Retrieve data from the BrentCrudeData model
    brent_crude_data = BrentCrudeData.objects.filter(
        date__gte=start_time,
        date__lte=end_time
    ).order_by('date')  # Order by date

    # Serialize the data
    serializer = BrentCrudeDataSerializer(brent_crude_data, many=True)

    # Return the serialized data as JSON response
    return Response(serializer.data)


@api_view(['GET'])
def get_geopolitical_news(request):
    # Define your search keywords for geopolitical risks
    keywords = ['']

    # Create a Q object for OR logic between the keywords
    query = Q(title__icontains=keywords[0])
    for keyword in keywords[1:]:
        query |= Q(title__icontains=keyword)

    # Retrieve the news data that matches the keywords
    news_data = GeopoliticalNews.objects.filter(query).order_by('-published_at')[:20]  # Get the most recent 20 articles

    # Serialize the data using GeopoliticalNewsSerializer
    serializer = GeopoliticalNewsSerializer(news_data, many=True)

    # Return the serialized data as JSON response
    return Response(serializer.data)














