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
from django.http import HttpResponse, JsonResponse
from .firebase import db  # Import the Firestore client from firebase.py
from django.views.decorators.csrf import csrf_exempt
import json

# View for the homepage to display the historical data for all currency pairs
def home(request):
    end_time = timezone.now()
    start_time = end_time - timedelta(days=30)  # Get data for the last 30 days

    # Retrieve data for all currency pairs
    currency_data = CurrencyData.objects.filter(
        date__gte=start_time,
        date__lte=end_time
    ).order_by('currency_pair', 'date')

    # Group the data by currency pair
    grouped_data = {}
    for key, group in groupby(currency_data, lambda x: x.currency_pair):
        grouped_data[key] = list(group)

    # Round decimal fields to 3 places
    for currency_pair, entries in grouped_data.items():
        for entry in entries:
            entry.open_price = Decimal(entry.open_price).quantize(Decimal('0.001'), rounding=ROUND_DOWN)
            entry.high_price = Decimal(entry.high_price).quantize(Decimal('0.001'), rounding=ROUND_DOWN)
            entry.low_price = Decimal(entry.low_price).quantize(Decimal('0.001'), rounding=ROUND_DOWN)
            entry.close_price = Decimal(entry.close_price).quantize(Decimal('0.001'), rounding=ROUND_DOWN)
            entry.volume = Decimal(entry.volume).quantize(Decimal('0.001'), rounding=ROUND_DOWN)

    context = {
        "grouped_data": grouped_data
    }

    return render(request, 'home.html', context)


# API endpoint to return all currency data as JSON
@api_view(['GET'])
def get_currency_data(request):
    end_time = timezone.now()
    start_time = end_time - timedelta(days=30)

    # Retrieve data for all currency pairs
    currency_data = CurrencyData.objects.filter(
        date__gte=start_time,
        date__lte=end_time
    ).order_by('currency_pair', 'date')

    # Serialize and return the data
    serializer = CurrencyDataSerializer(currency_data, many=True)
    return Response(serializer.data)

# API endpoint for Brent Crude data
@api_view(['GET'])
def get_brent_crude_data(request):
    end_time = timezone.now()
    start_time = end_time - timedelta(days=30)

    # Retrieve Brent Crude data
    brent_crude_data = BrentCrudeData.objects.filter(
        date__gte=start_time,
        date__lte=end_time
    ).order_by('date')

    serializer = BrentCrudeDataSerializer(brent_crude_data, many=True)
    return Response(serializer.data)


# API endpoint for Geopolitical news
@api_view(['GET'])
def get_geopolitical_news(request):
    keywords = ['']  # Define your search keywords

    # Build the query for filtering based on the keywords
    query = Q(title__icontains=keywords[0])
    for keyword in keywords[1:]:
        query |= Q(title__icontains=keyword)

    # Retrieve and return news data
    news_data = GeopoliticalNews.objects.filter(query).order_by('-published_at')[:20]
    serializer = GeopoliticalNewsSerializer(news_data, many=True)
    return Response(serializer.data)

@csrf_exempt
def add_production_row(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)  # Ensures JSON format
            doc_ref = db.collection('ProductionForecasts').add(data)
            return JsonResponse({"message": "Data added successfully", "id": doc_ref.id}, status=201)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    print(request.body)
    return JsonResponse({"message": "Only POST method is allowed"}, status=405)
    


@csrf_exempt
def delete_production_row(request, doc_id):
    if request.method == 'DELETE':
        try:
            doc_ref = db.collection('ProductionForecasts').document(doc_id)
            doc_ref.delete()
            return JsonResponse({"message": "Data deleted successfully"}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"message": "Only DELETE method is allowed"}, status=405)
    

















