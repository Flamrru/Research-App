import pandas as pd
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import os
import json

def test_firebase_connection():
    """
    Test if Firebase connection is working properly.
    Returns True if successful, False otherwise.
    """
    try:
        # Initialize Firebase if not already initialized
        try:
            firebase_admin.get_app()
            print("Firebase already initialized")
        except ValueError:
            # Initialize with environment variables
            print("Initializing Firebase...")
            
            # Check if all required environment variables are set
            required_vars = [
                "FIREBASE_PROJECT_ID",
                "FIREBASE_PRIVATE_KEY_ID",
                "FIREBASE_PRIVATE_KEY",
                "FIREBASE_CLIENT_EMAIL",
                "FIREBASE_CLIENT_ID",
                "FIREBASE_CLIENT_X509_CERT_URL"
            ]
            
            # Check if we're in Replit
            if os.environ.get("REPL_ID") and not os.environ.get("FIREBASE_PROJECT_ID"):
                print("Running in Replit, checking for secrets...")
                # Secrets in Replit are automatically loaded as environment variables
            
            missing_vars = [var for var in required_vars if not os.environ.get(var)]
            if missing_vars:
                print(f"Missing environment variables: {', '.join(missing_vars)}")
                print("Please add these as Secrets in the Replit Secrets tab")
                return False
            
            # Initialize Firebase with credentials from environment variables
            cred = credentials.Certificate({
                "type": "service_account",
                "project_id": os.environ.get("FIREBASE_PROJECT_ID"),
                "private_key_id": os.environ.get("FIREBASE_PRIVATE_KEY_ID"),
                "private_key": os.environ.get("FIREBASE_PRIVATE_KEY").replace("\\n", "\n"),
                "client_email": os.environ.get("FIREBASE_CLIENT_EMAIL"),
                "client_id": os.environ.get("FIREBASE_CLIENT_ID"),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": os.environ.get("FIREBASE_CLIENT_X509_CERT_URL")
            })
            firebase_admin.initialize_app(cred)
            print("Firebase initialized successfully")
        
        # Test accessing Firestore
        db = firestore.client()
        print("Successfully connected to Firestore")
        
        # Try to fetch some data
        docs = db.collection('researchData').limit(1).get()
        if len(docs) > 0:
            print(f"Successfully retrieved data: {docs[0].to_dict()}")
        else:
            print("No data found in the researchData collection")
        
        return True
    
    except Exception as e:
        print(f"Firebase connection test failed: {e}")
        return False

def load_data_from_firebase():
    """
    Load research data from Firebase.
    Returns a pandas DataFrame with the data.
    """
    try:
        # Initialize Firebase if not already initialized
        try:
            firebase_admin.get_app()
        except ValueError:
            # Check if all required environment variables are set
            required_vars = [
                "FIREBASE_PROJECT_ID",
                "FIREBASE_PRIVATE_KEY_ID",
                "FIREBASE_PRIVATE_KEY",
                "FIREBASE_CLIENT_EMAIL",
                "FIREBASE_CLIENT_ID",
                "FIREBASE_CLIENT_X509_CERT_URL"
            ]
            
            # Check if we're in Replit
            if os.environ.get("REPL_ID") and not os.environ.get("FIREBASE_PROJECT_ID"):
                print("Running in Replit, checking for secrets...")
                # In Replit, secrets are automatically loaded as environment variables
            
            missing_vars = [var for var in required_vars if not os.environ.get(var)]
            if missing_vars:
                print(f"Missing environment variables: {', '.join(missing_vars)}")
                print("Please add these as Secrets in the Replit Secrets tab")
                return pd.DataFrame()  # Return empty DataFrame if missing variables
            
            # Initialize with environment variables
            cred = credentials.Certificate({
                "type": "service_account",
                "project_id": os.environ.get("FIREBASE_PROJECT_ID"),
                "private_key_id": os.environ.get("FIREBASE_PRIVATE_KEY_ID"),
                "private_key": os.environ.get("FIREBASE_PRIVATE_KEY").replace("\\n", "\n"),
                "client_email": os.environ.get("FIREBASE_CLIENT_EMAIL"),
                "client_id": os.environ.get("FIREBASE_CLIENT_ID"),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": os.environ.get("FIREBASE_CLIENT_X509_CERT_URL")
            })
            firebase_admin.initialize_app(cred)
        
        # Access Firestore and get data
        db = firestore.client()
        docs = db.collection('researchData').where('isPubliclyViewable', '==', True).get()
        
        # Convert to list of dictionaries
        data_list = [doc.to_dict() for doc in docs]
        
        # Return as DataFrame
        return pd.DataFrame(data_list)
    
    except Exception as e:
        print(f"Error loading data from Firebase: {e}")
        return pd.DataFrame()  # Return empty DataFrame on error

if __name__ == "__main__":
    # Test the Firebase connection
    if test_firebase_connection():
        print("\nFirebase connection test passed!")
        
        # Try to load data
        df = load_data_from_firebase()
        if not df.empty:
            print(f"\nSuccessfully loaded {len(df)} records from Firebase")
            print("\nSample data:")
            print(df.head())
        else:
            print("\nNo data loaded from Firebase")
    else:
        print("\nFirebase connection test failed!") 