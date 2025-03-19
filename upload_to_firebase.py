import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import json
import os
import pandas as pd
import argparse

def load_json_data(file_path):
    """Load data from the JSON file."""
    with open(file_path, 'r') as f:
        return json.load(f)

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
            try:
                year = int(year)
                
                # Process each pathogen
                for i, pathogen in enumerate(pathogens):
                    # Calculate indices for negative and positive values
                    col_idx = 1 + i * 2  # Starting index for each pathogen (negative)
                    
                    # Extract values, handling None values
                    try:
                        negative = 0 if pd.isna(row[col_idx]) else int(row[col_idx])
                        positive = 0 if pd.isna(row[col_idx + 1]) else int(row[col_idx + 1])
                    except:
                        negative = 0
                        positive = 0
                    
                    unknown = 0  # We'll use 0 for unknown since it's not in the data
                    
                    # Add to data list if there's any data
                    if negative > 0 or positive > 0:
                        data_list.append({
                            "Year": year,
                            "Pathogen": pathogen,
                            "Positive": positive,
                            "Negative": negative,
                            "Unknown": unknown,
                            "isPubliclyViewable": True
                        })
            except Exception as e:
                print(f"Error processing row with year {year}: {e}")
    
    return data_list

def upload_to_firebase(json_data, collection_name):
    """Upload the research data to Firebase Firestore."""
    # Process the raw JSON data to create documents
    processed_data = process_research_data(json_data)
    
    if not processed_data:
        print("No data to upload after processing")
        return []
    
    print(f"Processed {len(processed_data)} data points for upload")
    
    # Initialize Firebase Admin with credentials from environment variables
    # You'll need to set these up as environment variables
    try:
        # Check if already initialized
        firebase_admin.get_app()
    except ValueError:
        # Initialize the app
        print("Initializing Firebase...")
        
        # Check for required environment variables
        required_vars = [
            "FIREBASE_PROJECT_ID",
            "FIREBASE_PRIVATE_KEY_ID",
            "FIREBASE_PRIVATE_KEY",
            "FIREBASE_CLIENT_EMAIL",
            "FIREBASE_CLIENT_ID",
            "FIREBASE_CLIENT_X509_CERT_URL"
        ]
        
        missing_vars = [var for var in required_vars if not os.environ.get(var)]
        if missing_vars:
            print(f"Missing environment variables: {', '.join(missing_vars)}")
            print("Please set all required environment variables before running this script.")
            return []
        
        try:
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
        except Exception as e:
            print(f"Firebase initialization error: {e}")
            return []
    
    # Access Firestore
    db = firestore.client()
    print("Connected to Firestore database")
    
    # Check if collection already has data
    existing_docs = db.collection(collection_name).limit(1).get()
    if len(existing_docs) > 0:
        print(f"Warning: Collection '{collection_name}' already contains data.")
        if input("Do you want to continue and potentially add duplicate data? (y/n): ").lower() != 'y':
            print("Upload cancelled.")
            return []
    
    # Upload each document in batches (Firestore has a limit of 500 operations per batch)
    batch_size = 450  # Slightly under the 500 limit to be safe
    total_uploaded = 0
    
    for i in range(0, len(processed_data), batch_size):
        # Create a new batch
        batch = db.batch()
        batch_data = processed_data[i:i + batch_size]
        
        for j, item in enumerate(batch_data):
            # Create a unique document ID
            doc_ref = db.collection(collection_name).document(f"data_{i+j}")
            batch.set(doc_ref, item)
        
        # Commit the batch
        batch.commit()
        total_uploaded += len(batch_data)
        print(f"Uploaded batch of {len(batch_data)} documents. Total: {total_uploaded}/{len(processed_data)}")
    
    print(f"Successfully uploaded {total_uploaded} documents to collection '{collection_name}'")
    return processed_data

def main():
    parser = argparse.ArgumentParser(description='Upload research data to Firebase')
    parser.add_argument('--file', default='data_raw e.json', help='Path to the JSON data file')
    parser.add_argument('--collection', default='researchData', help='Firestore collection name to store the data')
    args = parser.parse_args()
    
    print(f"Loading data from {args.file}...")
    try:
        # Load and upload the data
        raw_data = load_json_data(args.file)
        processed_data = upload_to_firebase(raw_data, args.collection)
        
        if processed_data:
            print(f"Upload complete. {len(processed_data)} items stored in '{args.collection}' collection.")
            
            # Create a pandas DataFrame for verification
            df = pd.DataFrame(processed_data)
            print("\nData summary:")
            print(f"Years: {sorted(df['Year'].unique())}")
            print(f"Pathogens: {sorted(df['Pathogen'].unique())}")
            print(f"Total positive tests: {df['Positive'].sum()}")
            print(f"Total negative tests: {df['Negative'].sum()}")
            
            print("\nSample data (first 5 rows):")
            print(df.head())
        else:
            print("No data was uploaded.")
    
    except Exception as e:
        print(f"Error during upload process: {e}")

if __name__ == "__main__":
    main() 