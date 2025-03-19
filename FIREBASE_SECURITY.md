# Firebase Security Guide

This guide explains how to secure your Firebase Firestore data so it can only be accessed through your app.

## Current Security Implementation

Your Firebase data is secured through several layers:

1. **Firebase Security Rules**: Rules that specify who can read/write to your database
2. **Service Account Authentication**: Using Firebase Admin SDK with service account credentials
3. **Environment Variables**: Storing sensitive credentials in environment variables
4. **Public Visibility Flag**: Using `isPubliclyViewable` field to control access

## Setup Steps

### 1. Deploy Firebase Security Rules

Run the deployment script to apply security rules to your Firebase project:

```bash
python deploy_firebase_rules.py
```

This script will:
- Check if Firebase CLI is installed (install if needed)
- Log you into Firebase
- Create necessary Firebase project files
- Deploy the security rules defined in `firebase_security_rules.rules`

### 2. Protect Your .env File

Your `.env` file contains sensitive credentials. Make sure to:

- Never commit it to public repositories
- Add it to `.gitignore` (already done in your project)
- Set these environment variables in your deployment environment (like Replit)

### 3. When Uploading Data

When uploading data to Firebase, always:

1. Run the `upload_to_firebase.py` script from a secure environment
2. Verify that the `isPubliclyViewable` flag is set correctly
3. Check the output to ensure data was properly uploaded

## For Replit Deployment

When deploying to Replit:

1. Add all your Firebase environment variables to Replit's Secrets tab:
   - `FIREBASE_PROJECT_ID`
   - `FIREBASE_PRIVATE_KEY_ID` 
   - `FIREBASE_PRIVATE_KEY`
   - `FIREBASE_CLIENT_EMAIL`
   - `FIREBASE_CLIENT_ID`
   - `FIREBASE_CLIENT_X509_CERT_URL`

2. Replit will automatically load these into the environment

## How It Works

Your data security works as follows:

1. **Private Default**: All Firebase data is denied access by default
2. **Service Account Access**: Your app uses a service account to authenticate with Firebase
3. **Rules Enforcement**: Security rules allow read access only for authenticated requests 
4. **Data Filtering**: The `isPubliclyViewable` flag ensures only public data is accessible

## Testing Security

To test if your security is working:

1. Run the Firebase Data Loader test: `python firebase_data_loader.py`
2. Try accessing your data through the Firebase console
3. Verify that only authenticated requests can access the data

## Security Recommendations

1. Rotate your service account credentials periodically
2. Always deploy with the latest security rules
3. Keep your environment variables secure
4. Consider adding user authentication for more granular control
5. Monitor Firebase access logs for suspicious activity 