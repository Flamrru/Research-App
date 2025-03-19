# Research Data Explorer

## Running the App with Streamlit

This application is designed to work with Streamlit. To run it locally:

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the Streamlit application:
   ```
   streamlit run app.py
   ```

3. The app will be available at http://localhost:8501

## Firebase Credentials

The app uses Firebase for data storage. The credentials are stored in `.streamlit/secrets.toml` for local development (this file is already in .gitignore). 

If you need to recreate the secrets file from your .env file:
```bash
python convert_env_to_toml.py
```

## Deployment to Streamlit Cloud

To deploy this app to Streamlit Cloud:

1. Push your code to a GitHub repository
2. Sign in to [Streamlit Cloud](https://streamlit.io/cloud)
3. Create a new app and connect it to your GitHub repository
4. Specify `app.py` as the main file to run
5. Add your Firebase credentials in the Streamlit Cloud secrets management section

# Research Data Visualization

A Streamlit web application for visualizing research data in 3D and 2D bar charts.

## Features

- Interactive 3D bar charts with customizable appearance
- 2D stacked bars and heatmaps for alternative views
- Time series visualization to see trends over time
- Summary statistics with detailed analysis
- Filters for years and pathogens
- Customizable colors, opacity, and layout
- Linear or logarithmic scale options
- Download data as CSV
- Raw data view option

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd <repository-directory>
```

2. Install the required packages:
```bash
pip install -r requirements.txt
```

## Usage

Run the Streamlit app:
```bash
streamlit run app.py
```

Open your browser and navigate to the URL shown in the console (usually `http://localhost:8501`).

## Customizing Your Data

The application includes hardcoded research data from `data_raw e.json`. The data shows positive and negative test results for various pathogens across multiple years.

If you want to use your own data:

1. Edit the `load_research_data()` function in `data.py`
2. Ensure your data has the following columns:
   - `Year`: The year of the observation
   - `Pathogen`: The pathogen name
   - `Positive`: The positive count for that year/pathogen
   - `Negative`: The negative count for that year/pathogen
   - `Unknown`: The unknown count (optional)

## App Controls

### Visualization Controls
- **Year Range**: Filter data by year range
- **Pathogens**: Select which pathogens to include
- **Chart Type**: Choose between 3D Bars, 2D Stacked Bars, Heatmap, Time Series, Pie Chart, or Summary Statistics

### Visual Customization
- **Bar Width**: Adjust the width of the bars
- **Bar Spacing**: Change the spacing between bar types
- **Opacity**: Change the transparency of the bars
- **Colors**: Customize colors for Positive, Negative, and Unknown data

### Advanced Options
- **Show Grid**: Toggle grid visibility
- **Show Values on Bars**: Display numerical values on the bars
- **Bar Mode**: Choose between grouped or stacked bars (2D view)
- **Scale Type**: Toggle between linear and logarithmic scale
- **Sort Data**: Sort data by year, positive count, negative count, or total count

### Camera View (3D only)
- **Camera X, Y, Z**: Adjust the camera position to change the viewing angle

## Deployment

### Deploy on Streamlit Cloud

1. Push your code to a GitHub repository
2. Connect your repository to [Streamlit Cloud](https://streamlit.io/cloud)
3. Deploy your app

### Firebase Integration (For Data Privacy)

This method keeps your sensitive research data secure while still allowing public access to your app.

#### Step 1: Set Up Firebase

1. Create a Firebase account at [firebase.google.com](https://firebase.google.com)
2. Create a new Firebase project
3. Set up Firestore Database (start in production mode)
4. Configure security rules to block direct access:
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
5. Create a service account key (Project Settings → Service accounts → Generate new private key)

#### Step 2: Upload Data to Firebase

1. Install firebase-admin: `pip install firebase-admin`
2. Set environment variables with your Firebase credentials:
   ```bash
   # For Linux/Mac
   export FIREBASE_PROJECT_ID="your-project-id"
   export FIREBASE_PRIVATE_KEY_ID="your-private-key-id"
   export FIREBASE_PRIVATE_KEY="your-private-key"
   export FIREBASE_CLIENT_EMAIL="your-client-email"
   export FIREBASE_CLIENT_ID="your-client-id"
   export FIREBASE_CLIENT_X509_CERT_URL="your-client-x509-cert-url"
   
   # For Windows
   set FIREBASE_PROJECT_ID=your-project-id
   set FIREBASE_PRIVATE_KEY_ID=your-private-key-id
   set FIREBASE_PRIVATE_KEY=your-private-key
   set FIREBASE_CLIENT_EMAIL=your-client-email
   set FIREBASE_CLIENT_ID=your-client-id
   set FIREBASE_CLIENT_X509_CERT_URL=your-client-x509-cert-url
   ```
3. Run the upload script: `python upload_to_firebase.py`

For more detailed instructions, see the [DEPLOY.md](DEPLOY.md) file. 