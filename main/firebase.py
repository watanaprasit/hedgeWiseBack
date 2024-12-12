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




