from firebase_admin import auth
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import firebase_admin
from firebase_admin import credentials, firestore
import os
from dotenv import load_dotenv

load_dotenv()


cred = credentials.Certificate(os.getenv('FIREBASE_KEY_PATH'))

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()


@csrf_exempt
def verify_firebase_token(request):
    # Get the Firebase ID token from the request
    firebase_token = request.headers.get('Authorization').split('Bearer ')[-1]

    try:
        # Verify the Firebase ID token
        decoded_token = auth.verify_id_token(firebase_token)
        user_id = decoded_token['uid']
        
        # Return user information
        return JsonResponse({"status": "success", "user_id": user_id})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)})




def initialize_counter():
    counter_ref = db.collection('counters').document('production_forecasts_counter')
    
    doc = counter_ref.get()
    
    if not doc.exists:
        counter_ref.set({
            'current_id': 1
        })
    else:
        print(f"Counter document exists. Current ID: {doc.to_dict()['current_id']}")
        
def initialize_asset_locations_counter():
    counter_ref = db.collection('counters').document('assets_locations_counter')
    
    doc = counter_ref.get()
    
    if not doc.exists:
        counter_ref.set({
            'current_id': 1
        })
    else:
        print(f"AssetsLocations counter exists. Current ID: {doc.to_dict()['current_id']}")
        
        
def initialize_cashflow_projections_counter():
    counter_ref = db.collection('counters').document('cashflow_projections_counter')

    doc = counter_ref.get()

    if not doc.exists:
        counter_ref.set({
            'current_id': 1
        })
    else:
        print(f"Cashflow Projections counter exists. Current ID: {doc.to_dict()['current_id']}")
        
        
def initialize_forward_contracts_counter():
    counter_ref = db.collection('counters').document('forward_contracts_counter')

    doc = counter_ref.get()

    if not doc.exists:
        counter_ref.set({
            'current_id': 1
        })
    else:
        print(f"Forward Contracts counter exists. Current ID: {doc.to_dict()['current_id']}")

initialize_counter()
initialize_asset_locations_counter()
initialize_cashflow_projections_counter()
initialize_forward_contracts_counter()






