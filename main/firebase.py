import firebase_admin
from firebase_admin import credentials, firestore, auth
import os
from dotenv import load_dotenv

load_dotenv()


cred = credentials.Certificate(os.getenv('FIREBASE_KEY_PATH'))

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()

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


# Firebase Authentication Functions

# Create a Firebase user
def create_user(email, password):
    try:
        user = auth.create_user(email=email, password=password)
        return f"User created successfully with UID: {user.uid}"
    except Exception as e:
        return f"Error creating user: {str(e)}"

# Delete a Firebase user by UID
def delete_user(uid):
    try:
        auth.delete_user(uid)
        return f"User with UID {uid} deleted successfully."
    except Exception as e:
        return f"Error deleting user: {str(e)}"

# Get user details by email
def get_user_by_email(email):
    try:
        user = auth.get_user_by_email(email)
        return {
            'uid': user.uid,
            'email': user.email,
            'display_name': user.display_name,
            'photo_url': user.photo_url
        }
    except Exception as e:
        return f"Error retrieving user: {str(e)}"

# Get user details by UID
def get_user_by_uid(uid):
    try:
        user = auth.get_user(uid)
        return {
            'uid': user.uid,
            'email': user.email,
            'display_name': user.display_name,
            'photo_url': user.photo_url
        }
    except Exception as e:
        return f"Error retrieving user: {str(e)}"



