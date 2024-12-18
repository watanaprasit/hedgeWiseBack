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
            # Load the data from the request
            data = json.loads(request.body)

            # Get the current counter value from Firestore
            counter_ref = db.collection('counters').document('production_forecasts_counter')
            doc = counter_ref.get()

            if doc.exists:
                # Get the current ID, increment it, and update the counter document
                current_id = doc.to_dict()['current_id']
                new_id = current_id + 1  # Increment the ID

                # Update the counter document with the new ID
                counter_ref.update({
                    'current_id': new_id
                })

                # Generate the custom document ID with the 'PF-' prefix
                custom_id = f"PF-{new_id:03d}"  # Format as PF-001, PF-002, etc.

                # Add the document with the custom ID to the ProductionForecasts collection
                doc_ref = db.collection('ProductionForecasts').document(custom_id).set(data)
                
                return JsonResponse({"message": "Data added successfully", "id": custom_id}, status=201)
            else:
                return JsonResponse({"error": "Counter document not found"}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    
    return JsonResponse({"message": "Only POST method is allowed"}, status=405)


@csrf_exempt  # Allow DELETE method
def delete_production_forecast(request, document_id):
    if request.method == 'DELETE':
        try:
            # Attempt to get the document from Firestore
            doc_ref = db.collection('ProductionForecasts').document(document_id)
            doc = doc_ref.get()

            if not doc.exists:
                return JsonResponse({'error': 'Document not found'}, status=404)
            
            # Delete the document from Firestore
            doc_ref.delete()
            return JsonResponse({'message': 'Document deleted successfully'}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid HTTP method'}, status=405)


@api_view(['GET'])
def get_production_forecast(request):
    try:
        # Fetch all documents from the ProductionForecasts collection
        production_forecasts_ref = db.collection('ProductionForecasts')
        docs = production_forecasts_ref.stream()
        
        # Create a list to store the document data
        forecast_data = []
        
        # Loop through the documents and get their data
        for doc in docs:
            forecast_data.append({
                'id': doc.id,  # Document ID
                'data': doc.to_dict()  # Document data
            })
        
        # Return the data as JSON
        return JsonResponse(forecast_data, safe=False, status=200)
    
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
@csrf_exempt
def add_asset_location(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            # Get the current counter value from Firestore
            counter_ref = db.collection('counters').document('assets_locations_counter')
            doc = counter_ref.get()

            if doc.exists:
                current_id = doc.to_dict()['current_id']
                new_id = current_id + 1

                # Update the counter document
                counter_ref.update({'current_id': new_id})

                # Custom document ID
                custom_id = f"AL-{new_id:03d}"  # Format as AL-001, AL-002, etc.

                # Add the document to the AssetsLocations collection
                db.collection('AssetsLocations').document(custom_id).set(data)

                return JsonResponse({"message": "Asset location added successfully", "id": custom_id}, status=201)
            else:
                return JsonResponse({"error": "Counter document not found"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"message": "Only POST method is allowed"}, status=405)

@csrf_exempt
def delete_asset_location(request, document_id):
    if request.method == 'DELETE':
        try:
            doc_ref = db.collection('AssetsLocations').document(document_id)
            doc = doc_ref.get()

            if not doc.exists:
                return JsonResponse({'error': 'Document not found'}, status=404)

            doc_ref.delete()
            return JsonResponse({'message': 'Asset location deleted successfully'}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid HTTP method'}, status=405)

@api_view(['GET'])
def get_asset_locations(request):
    try:
        asset_locations_ref = db.collection('AssetsLocations')
        docs = asset_locations_ref.stream()

        data = [{'id': doc.id, 'data': doc.to_dict()} for doc in docs]

        return JsonResponse(data, safe=False, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


















