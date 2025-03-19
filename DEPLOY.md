# Deploying to Replit

This document provides detailed instructions for deploying the Research Data Visualization dashboard to Replit.

## Why Replit?

Replit offers several advantages for deploying Streamlit applications:

1. Free hosting with minimal setup
2. Secure storage for sensitive credentials via Secrets
3. Easy integration with GitHub repositories
4. Always-on capability with Replit's Always On feature

## Prerequisites

Before you begin, make sure you have:

1. A GitHub account with this repository cloned or forked
2. A Replit account
3. A Firebase project with Firestore database set up

## Step 1: Prepare Your GitHub Repository

1. Ensure your code is pushed to GitHub
2. Make sure sensitive data is not included (like the raw data file and .env file)
3. Verify that `.gitignore` includes `.env` and any other sensitive files

## Step 2: Create a New Repl

1. Log in to [Replit](https://replit.com)
2. Click the "+ Create Repl" button
3. Select "Import from GitHub"
4. Paste your GitHub repository URL
5. Choose "Python" as the language
6. Click "Import from GitHub"

## Step 3: Set Up Firebase Secrets

Firebase credentials should be added as Secrets in Replit:

1. In your Repl, click on "Tools" in the left sidebar
2. Select "Secrets"
3. Add the following secrets with your Firebase credentials:
   - `FIREBASE_PROJECT_ID`: Your Firebase project ID
   - `FIREBASE_PRIVATE_KEY_ID`: Your private key ID
   - `FIREBASE_PRIVATE_KEY`: Your entire private key including BEGIN/END lines
   - `FIREBASE_CLIENT_EMAIL`: Your client email
   - `FIREBASE_CLIENT_ID`: Your client ID
   - `FIREBASE_CLIENT_X509_CERT_URL`: Your client X509 cert URL

**Important Note About FIREBASE_PRIVATE_KEY**: 
When adding your private key, make sure to include the entire key with line breaks. In the Replit Secrets UI, you can paste the key as-is, including the `-----BEGIN PRIVATE KEY-----` and `-----END PRIVATE KEY-----` lines.

## Step 4: Run the App

1. Click the "Run" button at the top of the Replit interface
2. The app should start with the configured Streamlit parameters
3. You'll see output in the console showing Firebase initialization and Streamlit starting
4. If successful, you'll see a webview with your app running

## Step 5: Make Your Repl Always On (Optional)

For free Replit users, your app will sleep after a period of inactivity. To keep it running continuously:

1. Click on the "Tools" button in the left sidebar
2. Select "Always On"
3. Toggle the switch to enable Always On
4. Note that with a free Replit account, you have limited Always On repls

## Troubleshooting

If you encounter issues with your deployment, check the following:

### Firebase Connection Issues

1. Verify all Firebase secrets are correctly added in Secrets
2. Check the console output for any Firebase initialization errors
3. Ensure your Firebase service account has the necessary permissions

### App Not Starting

1. Check that the `.replit` file is configured correctly with the proper run command
2. Verify that all dependencies are properly listed in `requirements.txt`
3. Look for any error messages in the console

### Missing Data

1. Confirm that your Firebase Firestore database contains the expected data
2. Check that the security rules allow your service account to read the data
3. Look for any error messages related to data loading in the console

## Updating Your Deployment

To update your deployed app:

1. Push changes to your GitHub repository
2. In Replit, click on the Git icon in the left sidebar
3. Click "Pull" to get the latest changes
4. Click "Run" to restart the app with the new changes

## Custom Domain (Optional)

To use a custom domain with your Replit app:

1. Navigate to your project's "Settings" page
2. Find the "Custom domains" section
3. Follow the instructions to connect your domain

## Need Help?

If you're experiencing issues with your deployment, you can:

1. Check the [Replit documentation](https://docs.replit.com)
2. Visit the [Streamlit community forum](https://discuss.streamlit.io)
3. Open an issue in the GitHub repository 