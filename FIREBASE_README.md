# Firebase Security Implementation

This document provides an overview of how Firebase security is implemented in this project.

## Files Overview

- `firebase_security_rules.rules` - Contains the Firebase security rules
- `deploy_firebase_rules.py` - Script to deploy the security rules to Firebase
- `test_firebase_security.py` - Script to test if the security rules are working
- `FIREBASE_SECURITY.md` - Detailed guide on securing your Firebase data

## Security Architecture

The security system follows these principles:

1. **Default Deny** - All access is denied by default
2. **Service Account Authentication** - Only your service account can write data
3. **Origin Verification** - Data can only be read from your app's domain
4. **API Key Authentication** - Requests must have a valid API key
5. **Public Flag Filtering** - Only data marked as public is accessible

## Quick Start

1. **Setup Environment**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Deploy Security Rules**:
   ```bash
   python deploy_firebase_rules.py
   ```

3. **Test Security**:
   ```bash
   python test_firebase_security.py
   ```

## Working with Secure Data

### Uploading Data

Use the `upload_to_firebase.py` script to upload data securely:

```bash
python upload_to_firebase.py --file your_data.json --collection researchData
```

### Reading Data in Your App

The `firebase_data_loader.py` file contains secure functions for loading data from Firebase.

### Deploying to Replit

When deploying to Replit, add all Firebase credentials as Secrets in the Replit environment.

## Security Best Practices

1. Never commit your `.env` file containing Firebase credentials
2. Regularly rotate your service account credentials
3. Use the `isPubliclyViewable` flag to control data visibility
4. Test security after any changes using the test script
5. Always access data through the Firebase Admin SDK 