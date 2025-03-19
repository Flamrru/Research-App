"""
Deploy Firebase Security Rules

This script deploys security rules to your Firebase project to ensure data security.
Run this script after setting up your Firebase project and uploading data.
"""

import os
import subprocess
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_firebase_cli():
    """Check if Firebase CLI is installed"""
    try:
        result = subprocess.run(['firebase', '--version'], 
                               capture_output=True, 
                               text=True)
        if result.returncode == 0:
            print(f"Firebase CLI detected: {result.stdout.strip()}")
            return True
        else:
            return False
    except FileNotFoundError:
        return False

def install_firebase_cli():
    """Install Firebase CLI if not already installed"""
    print("Firebase CLI not found. Installing...")
    try:
        subprocess.run(['npm', 'install', '-g', 'firebase-tools'], check=True)
        print("Firebase CLI installed successfully!")
        return True
    except Exception as e:
        print(f"Error installing Firebase CLI: {e}")
        return False

def login_to_firebase():
    """Login to Firebase"""
    print("Logging in to Firebase...")
    try:
        subprocess.run(['firebase', 'login'], check=True)
        return True
    except Exception as e:
        print(f"Error logging in to Firebase: {e}")
        return False

def create_firebase_project_files():
    """Create necessary Firebase project files"""
    project_id = os.getenv("FIREBASE_PROJECT_ID")
    
    # Create .firebaserc file
    firebaserc = {
        "projects": {
            "default": project_id
        }
    }
    
    with open('.firebaserc', 'w') as f:
        json.dump(firebaserc, f, indent=2)
    
    # Create firebase.json file
    firebase_json = {
        "firestore": {
            "rules": "firebase_security_rules.rules",
            "indexes": "firestore.indexes.json"
        }
    }
    
    with open('firebase.json', 'w') as f:
        json.dump(firebase_json, f, indent=2)
    
    # Create empty firestore.indexes.json file
    firestore_indexes = {
        "indexes": [],
        "fieldOverrides": []
    }
    
    with open('firestore.indexes.json', 'w') as f:
        json.dump(firestore_indexes, f, indent=2)
    
    print("Firebase project files created successfully!")

def deploy_security_rules():
    """Deploy security rules to Firebase"""
    print("Deploying security rules to Firebase...")
    try:
        subprocess.run(['firebase', 'deploy', '--only', 'firestore:rules'], check=True)
        print("Security rules deployed successfully!")
        return True
    except Exception as e:
        print(f"Error deploying security rules: {e}")
        return False

def main():
    print("==== Firebase Security Rules Deployment ====")
    
    # Check for required environment variables
    required_vars = ["FIREBASE_PROJECT_ID"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"Error: Missing environment variables: {', '.join(missing_vars)}")
        print("Please make sure your .env file contains all required variables.")
        return
    
    # Check and install Firebase CLI if needed
    if not check_firebase_cli():
        if not install_firebase_cli():
            print("Error: Failed to install Firebase CLI. Please install manually.")
            print("Run: npm install -g firebase-tools")
            return
    
    # Login to Firebase
    if not login_to_firebase():
        print("Error: Failed to login to Firebase.")
        print("Please run 'firebase login' manually.")
        return
    
    # Create Firebase project files
    create_firebase_project_files()
    
    # Deploy security rules
    if deploy_security_rules():
        print("\n====== Success! ======")
        print("Firebase security rules have been deployed.")
        print("Your data is now secured and can only be accessed by your app.")
    else:
        print("\n====== Deployment Failed ======")
        print("Please check the error messages above and try again.")

if __name__ == "__main__":
    main() 