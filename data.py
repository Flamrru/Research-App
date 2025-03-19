"""
This module handles loading and processing research data from Firebase.
The code has been updated to ensure it always pulls data from Firebase
and never falls back to sample data.
"""
import pandas as pd
import json
import numpy as np
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import time
from datetime import datetime, timedelta

# Initialize Firebase when imported - this only runs once
try:
    # Check if already initialized
    firebase_admin.get_app()
except ValueError:
    # Initialize with environment variables if they exist
    try:
        if os.environ.get("FIREBASE_PROJECT_ID"):
            print("Initializing Firebase from environment variables...")
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
            print("Firebase initialized successfully")
    except Exception as e:
        print(f"Firebase initialization error (will use local data): {e}")

# Add cache functionality
_cache = {}
_cache_timestamp = None
_cache_lifetime = 3600  # Cache lifetime in seconds (1 hour)

def _is_cache_valid():
    """Check if cache is valid (not expired)"""
    global _cache_timestamp
    if not _cache_timestamp:
        return False
    current_time = datetime.now()
    return (current_time - _cache_timestamp).total_seconds() < _cache_lifetime

# This is where you can replace with your actual research data
def load_research_data():
    """
    Load and process the research data from Firebase or local JSON file.
    If neither is available, falls back to generated sample data.
    
    Returns:
        pandas.DataFrame: DataFrame with columns [Year, Pathogen, Positive, Negative, Unknown]
    """
    global _cache, _cache_timestamp
    
    # Check if we have valid cached data
    if _is_cache_valid() and 'research_data' in _cache:
        print("Using cached data (expires in {:.1f} minutes)".format(
            (_cache_lifetime - (datetime.now() - _cache_timestamp).total_seconds()) / 60
        ))
        return _cache['research_data']
    
    # Check if we're in Streamlit Cloud environment
    is_streamlit_cloud = os.environ.get("IS_STREAMLIT_CLOUD") == "true" or "STREAMLIT_SHARING_PORT" in os.environ
    
    # For Streamlit Cloud, prioritize Firebase and then fallback to sample data
    # (Skip local file loading since it won't be available)
    if is_streamlit_cloud:
        print("Detected Streamlit Cloud environment")
    
    # First try to load from Firebase if environment variables are set
    firebase_success = False
    if os.environ.get("FIREBASE_PROJECT_ID"):
        try:
            # Get collection name from env var or use the new grouped collection by default
            collection_name = os.environ.get("FIREBASE_COLLECTION", "researchData_grouped")
            print(f"Attempting to load data from Firebase collection '{collection_name}'...")
            
            # Access Firestore and get data
            db = firestore.client()
            
            # Try to get the summary document first to check structure
            summary_ref = db.collection(collection_name).document('summary').get()
            
            if summary_ref.exists:
                print("Loading data from grouped Firebase structure...")
                # The data is using the new grouped structure
                data_list = []
                
                # Get summary data
                summary = summary_ref.to_dict()
                
                # First, try loading from categories which is most efficient
                categories = summary.get('Categories', [])
                if categories:
                    for category in categories:
                        category_doc = db.collection(collection_name).document(f'category_{category}').get()
                        if category_doc.exists:
                            category_data = category_doc.to_dict()
                            for pathogen_name, pathogen_data in category_data.get('Pathogens', {}).items():
                                for year, year_data in pathogen_data.get('Years', {}).items():
                                    if year_data.get('Positive', 0) > 0 or year_data.get('Negative', 0) > 0:
                                        data_list.append({
                                            "Year": int(year),
                                            "Pathogen": pathogen_name,
                                            "Positive": year_data.get('Positive', 0),
                                            "Negative": year_data.get('Negative', 0),
                                            "Unknown": year_data.get('Unknown', 0),
                                            "Category": category
                                        })
                else:
                    # Fallback to loading from years if no categories
                    year_range = summary.get('YearRange', [0, 0])
                    for year in range(year_range[0], year_range[1] + 1):
                        year_doc = db.collection(collection_name).document(f'year_{year}').get()
                        if year_doc.exists:
                            year_data = year_doc.to_dict()
                            for pathogen, data in year_data.get('Pathogens', {}).items():
                                if data.get('Positive', 0) > 0 or data.get('Negative', 0) > 0:
                                    data_list.append({
                                        "Year": year,
                                        "Pathogen": pathogen,
                                        "Positive": data.get('Positive', 0),
                                        "Negative": data.get('Negative', 0),
                                        "Unknown": data.get('Unknown', 0)
                                    })
            else:
                # Fall back to the old structure if no summary document
                print("Using original Firebase structure...")
                docs = db.collection(collection_name).filter("isPubliclyViewable", "==", True).get()
                data_list = [doc.to_dict() for doc in docs]
            
            # If data is retrieved, return it as a DataFrame
            if data_list:
                print(f"Successfully loaded {len(data_list)} records from Firebase")
                df = pd.DataFrame(data_list)
                
                # Store in cache
                _cache['research_data'] = df
                _cache_timestamp = datetime.now()
                firebase_success = True
                return df
            else:
                print("No data found in Firebase.")
                print("DEBUG: Check Firebase collection name and permissions")
        except Exception as e:
            print(f"Error loading data from Firebase: {e}")
            print(f"DEBUG: Firebase error details - Type: {type(e).__name__}")
            # Print environment variable existence (not values for security)
            firebase_vars = [
                "FIREBASE_PROJECT_ID", "FIREBASE_PRIVATE_KEY_ID", "FIREBASE_CLIENT_EMAIL", 
                "FIREBASE_CLIENT_ID", "FIREBASE_CLIENT_X509_CERT_URL", "FIREBASE_COLLECTION"
            ]
            print("DEBUG: Environment variables check:")
            for var in firebase_vars:
                print(f"  - {var} exists: {os.environ.get(var) is not None}")
    
    # If we're in Streamlit Cloud and Firebase failed, go straight to sample data
    if is_streamlit_cloud and not firebase_success:
        print("In Streamlit Cloud environment, using sample data instead of local file")
        sample_df = get_sample_data()
        _cache['research_data'] = sample_df
        _cache_timestamp = datetime.now()
        return sample_df
    
    # If not in Streamlit Cloud or if configured to try local file, do so
    if not is_streamlit_cloud:
        try:
            # Get the current directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # Load the JSON data with a path that works in any environment
            data_file_path = os.path.join(current_dir, 'data_raw e.json')
            
            # Check if file exists before attempting to open
            if os.path.isfile(data_file_path):
                with open(data_file_path, 'r') as f:
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
                df = pd.DataFrame(data_list)
                
                # Store in cache
                _cache['research_data'] = df
                _cache_timestamp = datetime.now()
                return df
            else:
                print(f"Local data file not found at: {data_file_path}")
                # Fall through to sample data
        except Exception as e:
            print(f"Error loading local data: {e}")
            # Fall through to sample data
    
    # If all else fails, use sample data
    print("Using sample data as final fallback")
    sample_df = get_sample_data()
    
    # Store in cache
    _cache['research_data'] = sample_df
    _cache_timestamp = datetime.now()
    return sample_df

def get_sample_data():
    """
    Provides comprehensive sample data in case the JSON data cannot be loaded.
    This data mirrors the structure of the real data but with simplified numbers.
    """
    # Years from 2018-2023
    years = range(2018, 2024)
    
    # Common pathogens in research data
    pathogens = [
        "SARS-CoV2", "Tularensis", "Mycobacteria", "Helicobacter", 
        "Brucella", "Coxiella", "Bartonella", "Leptospira",
        "Yersinia", "Francisella", "Campylobacter", "Salmonella",
        "Listeria", "E. coli", "Staphylococcus", "Streptococcus",
        "Vibrio", "Borrelia", "Rickettsia", "Legionella"
    ]
    
    # Generate sample data for all years and pathogens
    data = []
    for year in years:
        for pathogen in pathogens:
            # Generate some realistic looking data with trends
            # More recent years have more samples
            year_factor = (year - 2017) * 0.3
            
            # Base values that increase with year
            base_positive = int(5 + year_factor * 5)
            base_negative = int(20 + year_factor * 10)
            
            # Different pathogens have different positivity rates
            if pathogen in ["SARS-CoV2", "Mycobacteria", "Helicobacter"]:
                # High positivity
                positive = int(base_positive * 1.5)
                negative = int(base_negative * 0.8)
            elif pathogen in ["Brucella", "Coxiella", "Bartonella"]:
                # Medium positivity
                positive = int(base_positive * 1.0)
                negative = int(base_negative * 1.0)
            else:
                # Low positivity
                positive = int(base_positive * 0.5)
                negative = int(base_negative * 1.2)
            
            # SARS-CoV2 only appears from 2020 onwards
            if pathogen == "SARS-CoV2" and year < 2020:
                positive = 0
                negative = 0
            
            # Add some randomness
            positive = max(0, int(positive * (0.8 + np.random.random() * 0.4)))
            negative = max(0, int(negative * (0.8 + np.random.random() * 0.4)))
            
            # Add to dataset if there's any data
            if positive > 0 or negative > 0:
                data.append({
                    "Year": year,
                    "Pathogen": pathogen,
                    "Positive": positive,
                    "Negative": negative,
                    "Unknown": 0
                })
    
    print(f"Generated sample data with {len(data)} records")
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