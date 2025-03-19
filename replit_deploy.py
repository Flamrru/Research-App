"""
Replit Deployment Helper

This script helps set up the environment for deploying the application on Replit.
It checks for Firebase credentials and sets up the environment for running the app.
"""

import os
import json
import sys
import subprocess

# Colors for terminal output
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"
BOLD = "\033[1m"

def print_header(text):
    """Print a formatted header"""
    print(f"\n{BOLD}{GREEN}=== {text} ==={RESET}\n")

def print_warning(text):
    """Print a warning message"""
    print(f"{YELLOW}WARNING: {text}{RESET}")

def print_error(text):
    """Print an error message"""
    print(f"{RED}ERROR: {text}{RESET}")

def print_success(text):
    """Print a success message"""
    print(f"{GREEN}✓ {text}{RESET}")

def is_running_on_replit():
    """Check if the script is running on Replit"""
    return "REPL_ID" in os.environ and "REPL_OWNER" in os.environ

def check_firebase_credentials():
    """Check if Firebase credentials are available"""
    print_header("Checking Firebase Credentials")
    
    # Check for credentials file
    if os.path.exists("firebase-credentials.json"):
        with open("firebase-credentials.json", "r") as f:
            creds = json.load(f)
            print_success("Found firebase-credentials.json file")
            return True
    
    # Check for environment variables
    required_vars = [
        "FIREBASE_PROJECT_ID",
        "FIREBASE_PRIVATE_KEY_ID",
        "FIREBASE_PRIVATE_KEY",
        "FIREBASE_CLIENT_EMAIL",
        "FIREBASE_CLIENT_ID",
        "FIREBASE_CLIENT_X509_CERT_URL"
    ]
    
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if not missing_vars:
        print_success("All required Firebase environment variables are set")
        return True
    
    if is_running_on_replit():
        print_error(f"Missing Firebase environment variables: {', '.join(missing_vars)}")
        print("Please set these in the Replit Secrets tab (Tools > Secrets)")
        print("For instructions, see the DEPLOY.md file")
    else:
        print_error(f"Missing Firebase environment variables: {', '.join(missing_vars)}")
        print("Please set these in your .env file or as environment variables")
    
    return False

def install_dependencies():
    """Install required dependencies"""
    print_header("Installing Dependencies")
    
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print_success("Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to install dependencies: {e}")
        return False

def setup_replit_environment():
    """Set up the Replit environment"""
    if not is_running_on_replit():
        print_warning("Not running on Replit, skipping Replit-specific setup")
        return True
    
    print_header("Setting Up Replit Environment")
    
    # Check if .replit file exists
    if not os.path.exists(".replit"):
        print("Creating .replit file...")
        with open(".replit", "w") as f:
            f.write("""
[entrypoint]
command = "python -m streamlit run app.py --server.headless true --server.enableCORS false --server.enableXsrfProtection false"

[env]
PYTHONPATH = "${PYTHONPATH}:${REPL_HOME}"

[nix]
channel = "stable-22_11"

[languages]
[languages.python3]
pattern = "**/*.py"
syntax = "python"
""")
        print_success("Created .replit file")
    else:
        print_success(".replit file already exists")
    
    # Check if replit.nix file exists
    if not os.path.exists("replit.nix"):
        print("Creating replit.nix file...")
        with open("replit.nix", "w") as f:
            f.write("""
{ pkgs }: {
    deps = [
        pkgs.python310
        pkgs.replitPackages.prybar-python310
        pkgs.replitPackages.stderred
    ];
    env = {
        PYTHON_LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
            pkgs.stdenv.cc.cc.lib
        ];
        PYTHONHOME = "${pkgs.python310}";
        PYTHONBIN = "${pkgs.python310}/bin/python3.10";
        LANG = "en_US.UTF-8";
        STDERREDBIN = "${pkgs.replitPackages.stderred}/bin/stderred";
        PRYBAR_PYTHON_BIN = "${pkgs.replitPackages.prybar-python310}/bin/prybar-python310";
    };
}
""")
        print_success("Created replit.nix file")
    else:
        print_success("replit.nix file already exists")
    
    return True

def run_app():
    """Run the Streamlit app"""
    print_header("Running Streamlit App")
    
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py", 
                      "--server.headless", "true", 
                      "--server.enableCORS", "false", 
                      "--server.enableXsrfProtection", "false"], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to run the Streamlit app: {e}")
        return False
    except KeyboardInterrupt:
        print("\nApp stopped by user")
        return True

def main():
    print(f"\n{BOLD}{GREEN}=== RESEARCH DATA VISUALIZATION APP DEPLOYMENT ==={RESET}\n")
    
    # Check Firebase credentials
    if not check_firebase_credentials():
        if not is_running_on_replit():
            print("Creating a sample credentials file for testing...")
            # This is just for testing, not for production use
            sample_creds = {
                "type": "service_account",
                "project_id": "sample-project",
                "private_key_id": "sample",
                "private_key": "-----BEGIN PRIVATE KEY-----\nsample\n-----END PRIVATE KEY-----\n",
                "client_email": "sample@sample.com",
                "client_id": "123456789",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/sample"
            }
            with open("firebase-credentials.json", "w") as f:
                json.dump(sample_creds, f, indent=2)
            print_warning("Created a sample credentials file for testing purposes")
            print_warning("This is NOT suitable for production use")
            print_warning("The app will fall back to local data")
        else:
            print_error("Cannot proceed without Firebase credentials")
            print("Please set up the Firebase credentials in the Replit Secrets tab")
            print("For instructions, see the DEPLOY.md file")
            return
    
    # Install dependencies
    if not install_dependencies():
        print_error("Failed to install dependencies, cannot proceed")
        return
    
    # Set up Replit environment
    if not setup_replit_environment():
        print_error("Failed to set up Replit environment")
        return
    
    # Run the app
    print(f"\n{BOLD}{GREEN}=== DEPLOYMENT SUCCESSFUL ==={RESET}\n")
    print("You can now run the app with: streamlit run app.py")
    
    if is_running_on_replit():
        print("Or access it via the Replit webview")
    
    # Ask if user wants to run the app now
    if input("Run the app now? (y/n): ").lower() == 'y':
        run_app()

if __name__ == "__main__":
    main() 