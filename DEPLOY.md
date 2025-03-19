# Detailed Deployment Guide: Streamlit Cloud

This guide provides step-by-step instructions for deploying your Research Data Visualization app to Streamlit Cloud while keeping your research data secure in Firebase.

## Overview

Your Streamlit application visualizes research data from a JSON file. To protect this data while still making the app publicly accessible, we'll:

1. Store the sensitive research data in Firebase Firestore (secure, access-controlled)
2. Modify the app to fetch data from Firebase instead of the local file
3. Deploy the app code (without the data file) to Streamlit Cloud via GitHub

## Prerequisites

- A GitHub account
- A Google account (for Firebase)
- Python installed on your local machine
- Git installed on your local machine

## Step 1: Set Up Firebase

1. **Create a Firebase Account and Project:**
   - Go to [firebase.google.com](https://firebase.google.com)
   - Sign in with your Google account
   - Click "Add project"
   - Enter a name for your project (e.g., "Research Data Viz")
   - You can disable Google Analytics for simplicity
   - Click "Create project"

2. **Set Up Firestore Database:**
   - In the Firebase console, click "Firestore Database" in the left sidebar
   - Click "Create database"
   - Select "Start in production mode" (more secure)
   - Choose a location closest to your users
   - Click "Enable"

3. **Configure Security Rules:**
   - In Firestore, click the "Rules" tab
   - Replace the existing rules with:
   ```
   rules_version = '2';
   service cloud.firestore {
     match /databases/{database}/documents {
       match /{document=**} {
         allow read, write: if false;
       }
     }
   }
   ```
   - Click "Publish"

4. **Create a Service Account:**
   - In the left sidebar, click the gear icon ⚙️ (Project settings)
   - Click the "Service accounts" tab
   - Under "Firebase Admin SDK", click "Generate new private key"
   - Click "Generate key" in the popup
   - Save the downloaded JSON file securely

## Step 2: Prepare Your Local Environment

1. **Install Required Packages:**
   ```bash
   pip install firebase-admin
   ```

2. **Set Environment Variables:**
   Open the downloaded service account JSON file and set the following environment variables:

   **For Mac/Linux:**
   ```bash
   export FIREBASE_PROJECT_ID="your-project-id"
   export FIREBASE_PRIVATE_KEY_ID="your-private-key-id"
   export FIREBASE_PRIVATE_KEY="your-private-key"
   export FIREBASE_CLIENT_EMAIL="your-client-email"
   export FIREBASE_CLIENT_ID="your-client-id"
   export FIREBASE_CLIENT_X509_CERT_URL="your-client-x509-cert-url"
   ```

   **For Windows:**
   ```bash
   set FIREBASE_PROJECT_ID=your-project-id
   set FIREBASE_PRIVATE_KEY_ID=your-private-key-id
   set FIREBASE_PRIVATE_KEY=your-private-key
   set FIREBASE_CLIENT_EMAIL=your-client-email
   set FIREBASE_CLIENT_ID=your-client-id
   set FIREBASE_CLIENT_X509_CERT_URL=your-client-x509-cert-url
   ```

## Step 3: Upload Your Data to Firebase

1. **Run the Upload Script:**
   ```bash
   python upload_to_firebase.py
   ```

2. **Verify in Firebase Console:**
   - Go to Firestore Database
   - Check that your research data appears in the "researchData" collection
   - Each document should have a field "isPubliclyViewable" set to true

## Step 4: Create a GitHub Repository

1. **Go to GitHub and Create a New Repository:**
   - Visit [github.com](https://github.com)
   - Click "New" to create a new repository
   - Name it (e.g., "research-data-viz")
   - Set it to private if you want more privacy
   - Click "Create repository"

2. **Initialize Your Local Git Repository:**
   ```bash
   git init
   ```

3. **Create a .gitignore File:**
   Create a file named `.gitignore` with the following content:
   ```
   # Sensitive data files
   data_raw e.json
   *.json
   
   # Python
   __pycache__/
   *.py[cod]
   *$py.class
   .Python
   .pytest_cache/
   .coverage
   htmlcov/
   .tox/
   .nox/
   .hypothesis/
   .venv/
   venv/
   env/
   
   # Streamlit
   .streamlit/secrets.toml
   
   # OS specific
   .DS_Store
   Thumbs.db
   
   # IDE specific
   .idea/
   .vscode/
   *.swp
   *.swo
   ```

4. **Add and Commit Your Files:**
   ```bash
   git add .
   git commit -m "Initial commit"
   ```

5. **Connect to Your GitHub Repository:**
   ```bash
   git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git
   git branch -M main
   git push -u origin main
   ```

## Step 5: Deploy to Streamlit Cloud

1. **Log in to Streamlit Cloud:**
   - Go to [streamlit.io](https://streamlit.io)
   - Sign in with your account

2. **Create a New Streamlit App from GitHub:**
   - Click "New App"
   - Go to the "Import from GitHub" tab
   - Paste your GitHub repository URL
   - Click "Import from GitHub"

3. **Set Up Environment Variables/Secrets in Streamlit:**
   - In your Streamlit app, click the lock 🔒 icon in the left sidebar
   - Add the following secrets (with values from your Firebase service account JSON):
     - Key: `FIREBASE_PROJECT_ID`, Value: (your project_id)
     - Key: `FIREBASE_PRIVATE_KEY_ID`, Value: (your private_key_id)
     - Key: `FIREBASE_PRIVATE_KEY`, Value: (your private_key, including BEGIN and END lines)
     - Key: `FIREBASE_CLIENT_EMAIL`, Value: (your client_email)
     - Key: `FIREBASE_CLIENT_ID`, Value: (your client_id)
     - Key: `FIREBASE_CLIENT_X509_CERT_URL`, Value: (your client_x509_cert_url)

4. **Run Your App:**
   - Click the "Run" button at the top of Streamlit
   - Your app should start and connect to Firebase to get your data
   - You should see the URL where your app is hosted in the right panel

## Troubleshooting

1. **Firebase Connection Issues:**
   - Check if all environment variables are set correctly
   - Ensure the private key includes the BEGIN and END lines
   - The private key needs to have \n characters replaced with actual newlines

2. **Data Not Loading:**
   - Check if the data was properly uploaded to Firebase
   - Verify the collection name is "researchData"
   - Make sure documents have "isPubliclyViewable" set to true

3. **Streamlit Errors:**
   - Check if firebase-admin is in your requirements.txt
   - Try restarting the streamlit

## Testing Your Deployment

1. **Test Firebase Connection:**
   You can run the following test script on Streamlit to verify your Firebase setup:
   ```bash
   python firebase_data_loader.py
   ```

2. **Test App Functionality:**
   - Open your app URL
   - Verify that all visualizations work correctly
   - Check that the data displayed matches your original data

## Updating Your App

When you need to update your app:

1. Make changes to your local code
2. Commit and push changes to GitHub:
   ```bash
   git add .
   git commit -m "Update description"
   git push
   ```
3. In Streamlit, click the "Pull" button (near the Version Control section)
4. Your app will automatically update with the changes

## Security Considerations

- Your research data is now stored in Firebase with strict security rules
- Only your server-side code with proper credentials can access the data
- The Firebase credentials are stored as encrypted Streamlit Secrets
- Your original data file is not uploaded to GitHub or Streamlit

## Additional Resources

- [Firebase Documentation](https://firebase.google.com/docs)
- [Streamlit Documentation](https://docs.streamlit.io)
- [GitHub Documentation](https://docs.github.com)

If you need to modify how Firebase data is accessed, edit the `load_research_data()` function in your `data.py` file. 