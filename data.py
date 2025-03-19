import pandas as pd
import json
import numpy as np
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# Initialize Firebase when imported - this can be skipped as we'll initialize in load_research_data

def load_research_data():
    """
    Load and process the research data from Firebase or local JSON file.
    
    Returns:
        pandas.DataFrame: DataFrame with columns [Year, Pathogen, Positive, Negative, Unknown]
    """
    # First try loading from Firebase using the credentials.json file
    try:
        # Initialize Firebase if not already initialized
        try:
            firebase_admin.get_app()
        except ValueError:
            try:
                # First try with the JSON credentials file
                if os.path.exists('firebase-credentials.json'):
                    cred = credentials.Certificate('firebase-credentials.json')
                    firebase_admin.initialize_app(cred)
                    print("Firebase initialized successfully with JSON credentials file")
                else:
                    # Fall back to environment variables
                    from dotenv import load_dotenv
                    load_dotenv()
                    
                    if os.environ.get("FIREBASE_PROJECT_ID"):
                        cred = credentials.Certificate({
                            "type": "service_account",
                            "project_id": os.environ.get("FIREBASE_PROJECT_ID"),
                            "private_key_id": os.environ.get("FIREBASE_PRIVATE_KEY_ID"),
                            "private_key": os.environ.get("FIREBASE_PRIVATE_KEY", "").replace("\\n", "\n"),
                            "client_email": os.environ.get("FIREBASE_CLIENT_EMAIL"),
                            "client_id": os.environ.get("FIREBASE_CLIENT_ID"),
                            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                            "token_uri": "https://oauth2.googleapis.com/token",
                            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                            "client_x509_cert_url": os.environ.get("FIREBASE_CLIENT_X509_CERT_URL")
                        })
                        firebase_admin.initialize_app(cred)
                        print("Firebase initialized successfully with environment variables")
                    else:
                        raise ValueError("No Firebase credentials found")
            except Exception as e:
                print(f"Firebase initialization error: {e}")
                print("Will fall back to local data")
                return load_local_data()
        
        # Try to load data from Firebase
        print("Loading data from Firebase...")
        db = firestore.client()
        docs = db.collection('researchData').where('isPubliclyViewable', '==', True).get()
        
        # Convert to list of dictionaries
        data_list = [doc.to_dict() for doc in docs]
        
        # If data is retrieved, return it as a DataFrame
        if data_list:
            print(f"Successfully loaded {len(data_list)} records from Firebase")
            
            # Convert to DataFrame
            df = pd.DataFrame(data_list)
            
            # Drop Firebase-specific fields that aren't needed for analysis
            if 'uploadedAt' in df.columns:
                df = df.drop(columns=['uploadedAt'])
            if 'batchId' in df.columns:
                df = df.drop(columns=['batchId'])
            if 'isPubliclyViewable' in df.columns:
                df = df.drop(columns=['isPubliclyViewable'])
                
            return df
        else:
            print("No data found in Firebase. Falling back to local data.")
            return load_local_data()
    
    except Exception as e:
        print(f"Error loading data from Firebase: {e}")
        print("Falling back to local data.")
        return load_local_data()

def load_local_data():
    """Load data from local JSON file"""
    try:
        # Load the JSON data
        with open('data_raw e.json', 'r') as f:
            raw_data = json.load(f)
        
        # Extract the headers
        pathogens = []
        for i in range(1, len(raw_data[1]), 2):
            if raw_data[1][i] and raw_data[1][i] != "(blank)" and not pd.isna(raw_data[1][i]):
                pathogens.append(raw_data[1][i])
        
        # Process the data rows (start from index 3 to skip headers)
        data_list = []
        
        for row in raw_data[3:-2]:  # Skip header rows and the last two rows (blank and grand total)
            year = row[0]
            if not pd.isna(year) and year != "(blank)":
                year = int(year)
                
                # Process each pathogen
                for i, pathogen in enumerate(pathogens):
                    # Calculate indices for negative and positive values
                    col_idx = 1 + i * 2  # Starting index for each pathogen (negative)
                    
                    # Extract values, handling NaN values
                    negative = 0 if pd.isna(row[col_idx]) else int(row[col_idx])
                    positive = 0 if pd.isna(row[col_idx + 1]) else int(row[col_idx + 1])
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
        
        print("Successfully loaded data from local file")
        return pd.DataFrame(data_list)
    
    except Exception as e:
        print(f"Error loading local data: {e}")
        # Return sample data if there's an error
        print("Using sample data as fallback")
        return get_sample_data()

def get_sample_data():
    """
    Provides sample data in case the JSON data cannot be loaded.
    """
    data = [
        # Excerpt of data
        {"Year": 2019, "Pathogen": "SARS-CoV2", "Positive": 0, "Negative": 0, "Unknown": 0},
        {"Year": 2020, "Pathogen": "SARS-CoV2", "Positive": 10, "Negative": 84, "Unknown": 0},
        {"Year": 2021, "Pathogen": "SARS-CoV2", "Positive": 18, "Negative": 83, "Unknown": 0},
        
        {"Year": 2018, "Pathogen": "Tularensis", "Positive": 3, "Negative": 22, "Unknown": 0},
        {"Year": 2019, "Pathogen": "Tularensis", "Positive": 4, "Negative": 29, "Unknown": 0},
        {"Year": 2020, "Pathogen": "Tularensis", "Positive": 6, "Negative": 22, "Unknown": 0},
        {"Year": 2021, "Pathogen": "Tularensis", "Positive": 24, "Negative": 27, "Unknown": 0},
        
        {"Year": 2018, "Pathogen": "Mycobacteria", "Positive": 15, "Negative": 99, "Unknown": 0},
        {"Year": 2019, "Pathogen": "Mycobacteria", "Positive": 14, "Negative": 112, "Unknown": 0},
        {"Year": 2020, "Pathogen": "Mycobacteria", "Positive": 25, "Negative": 104, "Unknown": 0},
        {"Year": 2021, "Pathogen": "Mycobacteria", "Positive": 21, "Negative": 155, "Unknown": 0},
        
        {"Year": 2018, "Pathogen": "Helicobacter", "Positive": 30, "Negative": 122, "Unknown": 0},
        {"Year": 2019, "Pathogen": "Helicobacter", "Positive": 30, "Negative": 121, "Unknown": 0},
        {"Year": 2020, "Pathogen": "Helicobacter", "Positive": 34, "Negative": 145, "Unknown": 0},
        {"Year": 2021, "Pathogen": "Helicobacter", "Positive": 44, "Negative": 118, "Unknown": 0},
    ]
    return pd.DataFrame(data)

# Helper function to get a complete dataframe with all year/pathogen combinations
def get_complete_data(df):
    """
    Ensures all pathogen/year combinations exist in the dataframe,
    filling missing combinations with zeros.
    """
    # Get all unique years and pathogens
    all_years = sorted(df["Year"].unique())
    all_pathogens = sorted(df["Pathogen"].unique())
    
    # Create a complete dataframe with all combinations
    complete_data = []
    for year in all_years:
        for pathogen in all_pathogens:
            # Check if this combination exists in the original data
            existing = df[(df["Year"] == year) & (df["Pathogen"] == pathogen)]
            
            if len(existing) > 0:
                # Use existing data
                row = existing.iloc[0].to_dict()
            else:
                # Create a new row with zeros
                row = {
                    "Year": year,
                    "Pathogen": pathogen,
                    "Positive": 0,
                    "Negative": 0,
                    "Unknown": 0
                }
            
            complete_data.append(row)
    
    return pd.DataFrame(complete_data) 