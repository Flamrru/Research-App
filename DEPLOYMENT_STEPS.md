# Deployment Steps for Research Data Visualization App

This guide provides simplified steps to deploy your application to GitHub and Replit, with Firebase integration for secure data storage.

## What We've Accomplished

1. ✅ Set up Firebase Security rules
2. ✅ Uploaded research data to Firebase
3. ✅ Modified app to load data from Firebase
4. ✅ Created deployment helpers for Replit

## Step 1: GitHub Repository Setup

1. Create a new GitHub repository at [github.com/new](https://github.com/new)
2. Initialize your local repository:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git
   git push -u origin main
   ```

## Step 2: Replit Deployment

1. Log in to [Replit](https://replit.com/)
2. Click "Create Repl" > "Import from GitHub"
3. Paste your GitHub repository URL and click "Import"
4. Add Firebase credentials as Secrets in Replit:
   - Go to "Tools" > "Secrets"
   - Add the following secrets:
     - `FIREBASE_PROJECT_ID`: `reaserch-project-1d8ca`
     - `FIREBASE_PRIVATE_KEY_ID`: `b148f2ada7d57ad511078ce9ddfc36145a7a8fb2`
     - `FIREBASE_PRIVATE_KEY`: The entire private key including `-----BEGIN PRIVATE KEY-----` and `-----END PRIVATE KEY-----`
     - `FIREBASE_CLIENT_EMAIL`: `firebase-adminsdk-fbsvc@reaserch-project-1d8ca.iam.gserviceaccount.com`
     - `FIREBASE_CLIENT_ID`: `110586720613534307715`
     - `FIREBASE_CLIENT_X509_CERT_URL`: The URL from your credentials
5. Run the deployment helper:
   ```bash
   python replit_deploy.py
   ```
6. Click "Run" to start the application

## Step 3: Verify Deployment

1. Test Firebase connectivity by checking if data loads from Firebase
2. Verify that security rules are working as expected
3. Test all app features with the loaded data

## Optional: Testing Security

Run the security test script to verify Firebase security:
```bash
python test_firebase_security_with_json.py
```

## Troubleshooting

### Data Not Loading
- Check if Firebase credentials are correct
- Verify that data was uploaded to Firebase
- Ensure Firebase security rules allow reading data

### Deployment Issues
- Make sure all dependencies are in requirements.txt
- Check if .replit and replit.nix files are correctly set up
- Verify that environment variables/secrets are properly configured 