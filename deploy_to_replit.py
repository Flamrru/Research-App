import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import json
import os
import argparse

def load_json_data(file_path):
    """Load data from the JSON file."""
    with open(file_path, 'r') as f:
        return json.load(f)

def upload_to_firebase(json_data, collection_name):
    """Upload the research data to Firebase Firestore."""
    # Initialize Firebase Admin with credentials from environment variables
    # You'll need to set these up in Replit Secrets
    try:
        # Check if already initialized
        firebase_admin.get_app()
    except ValueError:
        # Initialize the app
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
    
    # Access Firestore
    db = firestore.client()
    
    # Process the raw JSON data to create documents
    processed_data = process_research_data(json_data)
    
    # Upload each document
    batch = db.batch()
    for i, item in enumerate(processed_data):
        doc_ref = db.collection(collection_name).document(f"item_{i}")
        # Add isPubliclyViewable flag to each document
        item["isPubliclyViewable"] = True
        batch.set(doc_ref, item)
    
    # Commit the batch
    batch.commit()
    print(f"Successfully uploaded {len(processed_data)} documents to collection '{collection_name}'")
    return processed_data

def process_research_data(raw_data):
    """Process the raw JSON data into a format suitable for Firestore."""
    # Extract the headers (pathogens)
    pathogens = []
    for i in range(1, len(raw_data[1]), 2):
        if raw_data[1][i] and raw_data[1][i] != "(blank)" and raw_data[1][i] is not None:
            pathogens.append(raw_data[1][i])
    
    # Process the data rows (start from index 3 to skip headers)
    data_list = []
    
    for row in raw_data[3:-2]:  # Skip header rows and the last two rows (blank and grand total)
        year = row[0]
        if year is not None and year != "(blank)":
            year = int(year)
            
            # Process each pathogen
            for i, pathogen in enumerate(pathogens):
                # Calculate indices for negative and positive values
                col_idx = 1 + i * 2  # Starting index for each pathogen (negative)
                
                # Extract values, handling None values
                negative = 0 if row[col_idx] is None else int(row[col_idx])
                positive = 0 if row[col_idx + 1] is None else int(row[col_idx + 1])
                unknown = 0  # We'll use 0 for unknown since it's not in the data
                
                # Add to data list if there's any data
                if negative > 0 or positive > 0:
                    data_list.append({
                        "Year": year,
                        "Pathogen": pathogen,
                        "Positive": positive,
                        "Negative": negative,
                        "Unknown": unknown
                    })
    
    return data_list

def modify_data_py_for_firebase():
    """Modify data.py to use Firebase instead of local JSON file."""
    with open('data.py', 'r') as f:
        original_code = f.read()
    
    firebase_code = '''import pandas as pd
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import os
import json
import numpy as np

# Initialize Firebase when imported
try:
    # Check if already initialized
    firebase_admin.get_app()
except ValueError:
    # Initialize the app using environment variables
    try:
        cred = credentials.Certificate({
            "type": "service_account",
            "project_id": os.environ.get("FIREBASE_PROJECT_ID"),
            "private_key_id": os.environ.get("FIREBASE_PRIVATE_KEY_ID"),
            "private_key": os.environ.get("FIREBASE_PRIVATE_KEY").replace("\\\\n", "\\n"),
            "client_email": os.environ.get("FIREBASE_CLIENT_EMAIL"),
            "client_id": os.environ.get("FIREBASE_CLIENT_ID"),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": os.environ.get("FIREBASE_CLIENT_X509_CERT_URL")
        })
        firebase_admin.initialize_app(cred)
    except Exception as e:
        print(f"Firebase initialization error: {e}")

def load_research_data():
    """
    Load and process the research data from Firebase.
    
    Returns:
        pandas.DataFrame: DataFrame with columns [Year, Pathogen, Positive, Negative, Unknown]
    """
    try:
        # Get data from Firebase
        db = firestore.client()
        docs = db.collection('researchData').where('isPubliclyViewable', '==', True).get()
        
        # Convert to list of dictionaries
        data_list = [doc.to_dict() for doc in docs]
        
        # If data is retrieved, return it as a DataFrame
        if data_list:
            return pd.DataFrame(data_list)
        else:
            print("No data found in Firebase. Using sample data.")
            return get_sample_data()
            
    except Exception as e:
        print(f"Error loading data from Firebase: {e}")
        # Return sample data if there's an error
        return get_sample_data()

def get_sample_data():
    """
    Provides sample data in case the Firebase data cannot be loaded.
    """
    # This part stays the same as your original code
'''
    
    # Find where the original load_research_data function starts
    load_data_start = original_code.find("def load_research_data()")
    if load_data_start == -1:
        print("Could not find load_research_data function. Manual update needed.")
        return False
    
    # Find the sample data function
    sample_data_start = original_code.find("def get_sample_data()")
    if sample_data_start == -1:
        print("Could not find get_sample_data function. Manual update needed.")
        return False
    
    # Combine the new Firebase code with the rest of the original file
    remaining_code = original_code[sample_data_start:]
    new_code = firebase_code + remaining_code
    
    # Create a backup of the original file
    with open('data.py.bak', 'w') as f:
        f.write(original_code)
    
    # Write the new code
    with open('data.py', 'w') as f:
        f.write(new_code)
    
    print("Successfully modified data.py to use Firebase.")
    return True

def update_requirements():
    """Update requirements.txt to include Firebase."""
    with open('requirements.txt', 'r') as f:
        current_requirements = f.read()
    
    if 'firebase-admin' not in current_requirements:
        with open('requirements.txt', 'a') as f:
            f.write('\nfirebase-admin')
        print("Added firebase-admin to requirements.txt")
    else:
        print("firebase-admin already in requirements.txt")

def main():
    parser = argparse.ArgumentParser(description='Prepare app for Replit deployment with Firebase data storage')
    parser.add_argument('--upload', action='store_true', help='Upload data to Firebase')
    parser.add_argument('--update-code', action='store_true', help='Update data.py to use Firebase')
    args = parser.parse_args()
    
    if args.upload:
        # Load and upload the data
        raw_data = load_json_data('data_raw e.json')
        processed_data = upload_to_firebase(raw_data, 'researchData')
        print(f"Uploaded {len(processed_data)} documents to Firebase")
    
    if args.update_code:
        # Modify data.py to use Firebase
        modify_data_py_for_firebase()
        # Update requirements.txt
        update_requirements()
    
    if not (args.upload or args.update_code):
        print("No actions specified. Use --upload to upload data to Firebase or --update-code to modify code.")

if __name__ == "__main__":
    main() 