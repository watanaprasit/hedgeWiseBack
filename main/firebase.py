import firebase_admin
from firebase_admin import credentials, firestore
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Firebase
cred = credentials.Certificate(os.getenv('FIREBASE_KEY_PATH'))
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

# Firestore client reference
db = firestore.client()

# Firestore initialization for the counters document
def initialize_counter():
    counter_ref = db.collection('counters').document('production_forecasts_counter')
    
    # Check if the counter document exists
    doc = counter_ref.get()
    
    if not doc.exists:
        # Initialize the counter document with an ID of 1 if it doesn't exist
        counter_ref.set({
            'current_id': 1
        })
    else:
        # If it exists, log the current value for debugging (optional)
        print(f"Counter document exists. Current ID: {doc.to_dict()['current_id']}")
        
def initialize_asset_locations_counter():
    counter_ref = db.collection('counters').document('assets_locations_counter')
    
    # Check if the counter document exists
    doc = counter_ref.get()
    
    if not doc.exists:
        # Initialize the counter document with an ID of 1 if it doesn't exist
        counter_ref.set({
            'current_id': 1
        })
    else:
        # If it exists, log the current value for debugging (optional)
        print(f"AssetsLocations counter exists. Current ID: {doc.to_dict()['current_id']}")

# Initialize the counter when the app is started
initialize_counter()
initialize_asset_locations_counter()






