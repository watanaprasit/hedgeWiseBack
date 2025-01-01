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
import yfinance as yf


# Function to fetch and update currency data from Yahoo Finance
def fetch_currency_data():
    # Example: fetch exchange rates for currency pairs like 'EURUSD=X'
    currency_pairs = ['EURUSD=X', 'GBPUSD=X', 'USDJPY=X']  # Add your required currency pairs here
    currency_data = []

    for pair in currency_pairs:
        # Fetch data using yfinance
        ticker = yf.Ticker(pair)
        hist = ticker.history(period="1d")
        
        # Extract necessary data
        if not hist.empty:
            data = hist.iloc[0]
            currency_data.append({
                'currency_pair': pair,
                'open_price': data['Open'],
                'high_price': data['High'],
                'low_price': data['Low'],
                'close_price': data['Close'],
                'volume': data['Volume'],
                'date': timezone.now()  # You may want to adjust this to match your actual date range
            })

    return currency_data

# View for the homepage to display the historical data for all currency pairs
def home(request):
    end_time = timezone.now()
    start_time = end_time - timedelta(days=30)  # Get data for the last 30 days

    # Fetch currency data from Yahoo Finance and update database
    currency_data = fetch_currency_data()

    # Update database with new data (if necessary)
    for data in currency_data:
        CurrencyData.objects.create(
            currency_pair=data['currency_pair'],
            open_price=data['open_price'],
            high_price=data['high_price'],
            low_price=data['low_price'],
            close_price=data['close_price'],
            volume=data['volume'],
            date=data['date']
        )

    # Retrieve data from the database for the last 30 days
    currency_data_db = CurrencyData.objects.filter(
        date__gte=start_time,
        date__lte=end_time
    ).order_by('currency_pair', 'date')

    # Group the data by currency pair
    grouped_data = {}
    for key, group in groupby(currency_data_db, lambda x: x.currency_pair):
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


# API endpoint to return only the latest close data for each currency pair
@api_view(['GET'])
def get_currency_data(request):
    end_time = timezone.now()
    start_time = end_time - timedelta(days=30)

    # Fetch currency data from Yahoo Finance and update database
    currency_data = fetch_currency_data()

    # Update database with new data (if necessary)
    for data in currency_data:
        CurrencyData.objects.create(
            currency_pair=data['currency_pair'],
            open_price=data['open_price'],
            high_price=data['high_price'],
            low_price=data['low_price'],
            close_price=data['close_price'],
            volume=data['volume'],
            date=data['date']
        )

    # Retrieve the most recent close prices for each currency pair
    latest_data = []
    currency_pairs = CurrencyData.objects.filter(
        date__gte=start_time,
        date__lte=end_time
    ).values('currency_pair').distinct()

    for pair in currency_pairs:
        # Fetch the latest data for each currency pair
        latest_entry = CurrencyData.objects.filter(currency_pair=pair['currency_pair']) \
            .order_by('-date').first()

        if latest_entry:
            latest_data.append({
                'currency_pair': latest_entry.currency_pair,
                'open_price': latest_entry.open_price,
                'high_price': latest_entry.high_price,
                'low_price': latest_entry.low_price,
                'close_price': latest_entry.close_price,
                'volume': latest_entry.volume,
                'date': latest_entry.date
            })

    # Serialize and return only the latest close data for each currency pair
    return Response(latest_data)



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
            # Load the data from the request (could be a single asset or a list of assets)
            data = json.loads(request.body)

            # Check if the data is a list (multiple asset locations)
            if isinstance(data, list):
                # Get the current counter value from Firestore
                counter_ref = db.collection('counters').document('assets_locations_counter')
                doc = counter_ref.get()

                if doc.exists:
                    current_id = doc.to_dict()['current_id']
                    new_id = current_id

                    response_data = []
                    for asset in data:
                        new_id += 1
                        custom_id = f"AL-{new_id:03d}"  # Format as AL-001, AL-002, etc.

                        # Add the asset location document to the AssetsLocations collection
                        db.collection('AssetsLocations').document(custom_id).set(asset)

                        response_data.append({
                            "message": "Asset location added successfully",
                            "id": custom_id
                        })

                    # Update the counter document with the new ID
                    counter_ref.update({'current_id': new_id})

                    return JsonResponse(response_data, safe=False, status=201)
                else:
                    return JsonResponse({"error": "Counter document not found"}, status=400)
            else:
                return JsonResponse({"error": "Expected a list of asset locations"}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)
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
    
@csrf_exempt
def add_cashflow_projection(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            if isinstance(data, list):
                counter_ref = db.collection('counters').document('cashflow_projections_counter')
                doc = counter_ref.get()

                if doc.exists:
                    current_id = doc.to_dict()['current_id']
                    new_id = current_id

                    response_data = []
                    for asset in data:
                        new_id += 1
                        custom_id = f"CFP-{new_id:03d}" 

                        db.collection('CashflowProjections').document(custom_id).set(asset)

                        response_data.append({
                            "message": "Cashflow Projection added successfully",
                            "id": custom_id
                        })

                    counter_ref.update({'current_id': new_id})

                    return JsonResponse(response_data, safe=False, status=201)
                else:
                    return JsonResponse({"error": "Counter document not found"}, status=400)
            else:
                return JsonResponse({"error": "Expected a list of cashflow projections"}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"message": "Only POST method is allowed"}, status=405)


@csrf_exempt
def delete_cashflow_projection(request, document_id):
    if request.method == 'DELETE':
        try:
            doc_ref = db.collection('CashflowProjections').document(document_id)
            doc = doc_ref.get()

            if not doc.exists:
                return JsonResponse({'error': 'Document not found'}, status=404)

            doc_ref.delete()
            return JsonResponse({'message': 'Cashflow projection deleted successfully'}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid HTTP method'}, status=405)


@api_view(['GET'])
def get_cashflow_projections(request):
    try:
        asset_locations_ref = db.collection('CashflowProjections')
        docs = asset_locations_ref.stream()

        data = [{'id': doc.id, 'data': doc.to_dict()} for doc in docs]

        return JsonResponse(data, safe=False, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
    
@csrf_exempt
def add_forward_contract(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            if isinstance(data, list):
                counter_ref = db.collection('counters').document('forward_contracts_counter')
                doc = counter_ref.get()

                if doc.exists:
                    current_id = doc.to_dict()['current_id']
                    new_id = current_id

                    response_data = []
                    for asset in data:
                        new_id += 1
                        custom_id = f"FC-{new_id:03d}" 

                        db.collection('ForwardContracts').document(custom_id).set(asset)

                        response_data.append({
                            "message": "Forward Contract added successfully",
                            "id": custom_id
                        })

                    counter_ref.update({'current_id': new_id})

                    return JsonResponse(response_data, safe=False, status=201)
                else:
                    return JsonResponse({"error": "Counter document not found"}, status=400)
            else:
                return JsonResponse({"error": "Expected a list of forward contracts"}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"message": "Only POST method is allowed"}, status=405)


@csrf_exempt
def delete_forward_contract(request, document_id):
    if request.method == 'DELETE':
        try:
            doc_ref = db.collection('ForwardContracts').document(document_id)
            doc = doc_ref.get()

            if not doc.exists:
                return JsonResponse({'error': 'Document not found'}, status=404)

            doc_ref.delete()
            return JsonResponse({'message': 'Forward Contract deleted successfully'}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid HTTP method'}, status=405)


@api_view(['GET'])
def get_forward_contracts(request):
    try:
        asset_locations_ref = db.collection('ForwardContracts')
        docs = asset_locations_ref.stream()

        data = [{'id': doc.id, 'data': doc.to_dict()} for doc in docs]

        return JsonResponse(data, safe=False, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
    
@csrf_exempt
def modify_cashflow_projection(request, document_id):
    if request.method == 'PUT':  # Use PUT for updating an existing resource
        try:
            # Load the data from the request body
            data = json.loads(request.body)

            # Check if the document exists in the Firestore collection
            doc_ref = db.collection('CashflowProjections').document(document_id)
            doc = doc_ref.get()

            if not doc.exists:
                return JsonResponse({'error': 'Document not found'}, status=404)

            # Update the document with the new data
            doc_ref.update(data)

            return JsonResponse({'message': 'Cashflow Projection updated successfully', 'id': document_id}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({'error': 'Invalid HTTP method, only PUT allowed'}, status=405)


@csrf_exempt
def add_futures_contract(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            if isinstance(data, list):
                counter_ref = db.collection('counters').document('futures_contracts_counter')
                doc = counter_ref.get()

                if doc.exists:
                    current_id = doc.to_dict()['current_id']
                    new_id = current_id

                    response_data = []
                    for asset in data:
                        new_id += 1
                        custom_id = f"FC-{new_id:03d}" 

                        db.collection('FuturesContracts').document(custom_id).set(asset)

                        response_data.append({
                            "message": "Futures Contract added successfully",
                            "id": custom_id
                        })

                    counter_ref.update({'current_id': new_id})

                    return JsonResponse(response_data, safe=False, status=201)
                else:
                    return JsonResponse({"error": "Counter document not found"}, status=400)
            else:
                return JsonResponse({"error": "Expected a list of futures contracts"}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"message": "Only POST method is allowed"}, status=405)


@csrf_exempt
def delete_futures_contract(request, document_id):
    if request.method == 'DELETE':
        try:
            doc_ref = db.collection('FuturesContracts').document(document_id)
            doc = doc_ref.get()

            if not doc.exists:
                return JsonResponse({'error': 'Document not found'}, status=404)

            doc_ref.delete()
            return JsonResponse({'message': 'Futures Contract deleted successfully'}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid HTTP method'}, status=405)


@api_view(['GET'])
def get_futures_contracts(request):
    try:
        asset_locations_ref = db.collection('FuturesContracts')
        docs = asset_locations_ref.stream()

        data = [{'id': doc.id, 'data': doc.to_dict()} for doc in docs]

        return JsonResponse(data, safe=False, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def debug_view(request, document_id):
    return JsonResponse({'document_id': document_id}, status=200)
















