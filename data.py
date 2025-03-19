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
import streamlit as st

# Initialize Firebase when imported - this only runs once
try:
    # Check if already initialized
    firebase_admin.get_app()
except ValueError:
    # Initialize with Streamlit secrets or environment variables
    try:
        # Check if we're in Streamlit environment
        in_streamlit = 'STREAMLIT_SHARING_PORT' in os.environ or hasattr(st, 'secrets')
        
        # Get Firebase credentials from Streamlit secrets or environment variables
        if in_streamlit and hasattr(st, 'secrets'):
            print("Initializing Firebase from Streamlit secrets...")
            firebase_project_id = st.secrets.get("FIREBASE_PROJECT_ID")
            firebase_private_key_id = st.secrets.get("FIREBASE_PRIVATE_KEY_ID")
            firebase_private_key = st.secrets.get("FIREBASE_PRIVATE_KEY", "")
            firebase_client_email = st.secrets.get("FIREBASE_CLIENT_EMAIL")
            firebase_client_id = st.secrets.get("FIREBASE_CLIENT_ID")
            firebase_client_x509_cert_url = st.secrets.get("FIREBASE_CLIENT_X509_CERT_URL")
            firebase_collection = st.secrets.get("FIREBASE_COLLECTION", "researchData")
        else:
            print("Initializing Firebase from environment variables...")
            firebase_project_id = os.environ.get("FIREBASE_PROJECT_ID")
            firebase_private_key_id = os.environ.get("FIREBASE_PRIVATE_KEY_ID")
            firebase_private_key = os.environ.get("FIREBASE_PRIVATE_KEY", "")
            firebase_client_email = os.environ.get("FIREBASE_CLIENT_EMAIL")
            firebase_client_id = os.environ.get("FIREBASE_CLIENT_ID")
            firebase_client_x509_cert_url = os.environ.get("FIREBASE_CLIENT_X509_CERT_URL")
            firebase_collection = os.environ.get("FIREBASE_COLLECTION", "researchData")
        
        # Replace \\n with \n in private key (needed for both env vars and secrets)
        firebase_private_key = firebase_private_key.replace("\\n", "\n")
        
        if firebase_project_id:
            cred = credentials.Certificate({
                "type": "service_account",
                "project_id": firebase_project_id,
                "private_key_id": firebase_private_key_id,
                "private_key": firebase_private_key,
                "client_email": firebase_client_email,
                "client_id": firebase_client_id,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": firebase_client_x509_cert_url
            })
            firebase_admin.initialize_app(cred)
            print("Firebase initialized successfully")
        else:
            raise ValueError("Firebase credentials not found in secrets or environment variables")
    except Exception as e:
        print(f"Firebase initialization error: {e}")
        print("Unable to initialize Firebase - no data will be available")

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

def load_research_data():
    """
    Load and process the research data from Firebase.
    
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
    
    # Check if we're in Streamlit environment
    in_streamlit = 'STREAMLIT_SHARING_PORT' in os.environ or hasattr(st, 'secrets')
    
    if in_streamlit:
        print("Detected Streamlit environment")
    
    # Try to load from Firebase
    firebase_success = False
    try:
        # Get collection name from Streamlit secrets or environment variables
        if in_streamlit and hasattr(st, 'secrets'):
            collection_name = st.secrets.get("FIREBASE_COLLECTION", "researchData")
        else:
            collection_name = os.environ.get("FIREBASE_COLLECTION", "researchData")
            
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
            # If no summary document, use the direct collection approach
            print("Using original Firebase structure...")
            docs = db.collection(collection_name).where("isPubliclyViewable", "==", True).get()
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
            raise Exception("Failed to retrieve data from Firebase collection")
    except Exception as e:
        print(f"Error loading data from Firebase: {e}")
        print(f"DEBUG: Firebase error details - Type: {type(e).__name__}")
        
        # Check which credentials are available
        if in_streamlit and hasattr(st, 'secrets'):
            firebase_vars = [
                "FIREBASE_PROJECT_ID", "FIREBASE_PRIVATE_KEY_ID", "FIREBASE_CLIENT_EMAIL", 
                "FIREBASE_CLIENT_ID", "FIREBASE_CLIENT_X509_CERT_URL", "FIREBASE_COLLECTION"
            ]
            print("DEBUG: Streamlit secrets check:")
            for var in firebase_vars:
                print(f"  - {var} exists: {var in st.secrets}")
        else:
            firebase_vars = [
                "FIREBASE_PROJECT_ID", "FIREBASE_PRIVATE_KEY_ID", "FIREBASE_CLIENT_EMAIL", 
                "FIREBASE_CLIENT_ID", "FIREBASE_CLIENT_X509_CERT_URL", "FIREBASE_COLLECTION"
            ]
            print("DEBUG: Environment variables check:")
            for var in firebase_vars:
                print(f"  - {var} exists: {os.environ.get(var) is not None}")
        
        # Re-raise the exception to stop execution
        raise Exception(f"Failed to load data from Firebase: {e}")
    
    # If we get here, we were unable to load data from any source
    raise Exception("No data could be loaded from Firebase. Please check your connection and Firebase configuration.")

# We'll keep the get_sample_data function for testing purposes, but it will not be used
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
    Ensures all meaningful pathogen/year combinations exist in the dataframe.
    Only includes pathogens that have at least one record in the dataset.
    """
    # Get all unique years and pathogens
    all_years = sorted(df["Year"].unique())
    all_pathogens = sorted(df["Pathogen"].unique())
    
    # Create a dataframe with only meaningful combinations
    complete_data = []
    
    # First, include all existing data points
    for _, row in df.iterrows():
        complete_data.append(row.to_dict())
    
    # Track which combinations we've already added
    existing_combinations = set((row['Year'], row['Pathogen']) for row in complete_data)
    
    # For each pathogen, find years where it has data
    pathogen_years = {}
    for pathogen in all_pathogens:
        pathogen_df = df[df["Pathogen"] == pathogen]
        if not pathogen_df.empty:
            # Get the range of years for this pathogen
            min_year = pathogen_df["Year"].min()
            max_year = pathogen_df["Year"].max()
            pathogen_years[pathogen] = (min_year, max_year)
    
    # Fill in missing entries only within the years where a pathogen has been recorded
    for pathogen, (min_year, max_year) in pathogen_years.items():
        for year in all_years:
            # Only consider years in the pathogen's active range
            if min_year <= year <= max_year:
                # Check if this combination is already in the dataset
                if (year, pathogen) not in existing_combinations:
                    # Create a new row with zeros
                    row = {
                        "Year": year,
                        "Pathogen": pathogen,
                        "Positive": 0,
                        "Negative": 0,
                        "Unknown": 0
                    }
                    
                    # Add optional columns with default values from the most recent existing record
                    if complete_data:
                        for key, value in complete_data[0].items():
                            if key not in row:
                                row[key] = value
                    
                    complete_data.append(row)
                    existing_combinations.add((year, pathogen))
    
    result_df = pd.DataFrame(complete_data)
    print(f"Complete data created: {len(df)} original records expanded to {len(result_df)} records")
    return result_df 