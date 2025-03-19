# Research Data Visualization App

An interactive web application for visualizing and exploring research data securely stored in Firebase. This app allows users to analyze pathogen test results across different years.

## Features

- Interactive data visualization with Streamlit
- Secure data storage in Firebase Firestore
- Dynamic filtering and exploration of research data
- Multiple visualization types (heatmaps, time series, etc.)
- Responsive design that works on desktop and mobile

## Firebase Security Implementation

The app uses Firebase for secure data storage with the following security features:

1. **Default Deny** - All access is denied by default
2. **Service Account Authentication** - Only your service account can write data
3. **Origin Verification** - Data can only be read from your app's domain
4. **API Key Authentication** - Requests must have a valid API key
5. **Public Flag Filtering** - Only data marked as public is accessible

## Deployment Steps

### Step 1: GitHub Repository Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git
   cd YOUR-REPO-NAME
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Step 2: Firebase Setup

1. Deploy Firebase security rules:
   ```bash
   python deploy_firebase_rules.py
   ```

2. Upload sample data to Firebase (if needed):
   ```bash
   python upload_to_firebase.py --file your_data.json --collection researchData
   ```

### Step 3: Replit Deployment

1. Log in to [Replit](https://replit.com/)
2. Click "Create Repl" > "Import from GitHub"
3. Paste your GitHub repository URL and click "Import"
4. Add Firebase credentials as Secrets in Replit:
   - Go to "Tools" > "Secrets"
   - Add the following secrets:
     - `FIREBASE_PROJECT_ID`: Your Firebase project ID
     - `FIREBASE_PRIVATE_KEY_ID`: Your private key ID
     - `FIREBASE_PRIVATE_KEY`: The entire private key including `-----BEGIN PRIVATE KEY-----` and `-----END PRIVATE KEY-----`
     - `FIREBASE_CLIENT_EMAIL`: Your client email
     - `FIREBASE_CLIENT_ID`: Your client ID
     - `FIREBASE_CLIENT_X509_CERT_URL`: Your client X509 cert URL
5. Run the deployment helper:
   ```bash
   python replit_deploy.py
   ```
6. Click "Run" to start the application

## Local Development

To run the app locally:

1. Create a `.env` file with your Firebase credentials or place `firebase-credentials.json` in the project root
2. Install dependencies: `pip install -r requirements.txt`
3. Run the app: `streamlit run app.py`

## Security Best Practices

1. Never commit your `.env` file or firebase-credentials.json containing Firebase credentials
2. Regularly rotate your service account credentials
3. Use the `isPubliclyViewable` flag to control data visibility
4. Test security after any changes
5. Always access data through the Firebase Admin SDK

## Troubleshooting

### Data Not Loading
- Check if Firebase credentials are correct
- Verify that data was uploaded to Firebase
- Ensure Firebase security rules allow reading data

### Deployment Issues
- Make sure all dependencies are in requirements.txt
- Check if .replit and replit.nix files are correctly set up
- Verify that environment variables/secrets are properly configured

## License

This project is licensed under the MIT License - see the LICENSE file for details. 