# Research Data Visualization Dashboard

A Streamlit-based dashboard for visualizing and analyzing research data, with a focus on pathogen detection trends over time.

## Features

- Interactive data filtering and search
- Multiple visualization types (bar charts, heatmaps, pie charts, time series)
- Statistical analysis and summary
- Firebase integration for data storage
- Responsive design for different screen sizes

## Live Demo

You can access the live demo at: [Replit App URL - Update when deployed]

## Deployment on Replit

1. **Create a new Repl**
   - Click "+ Create Repl"
   - Select "Import from GitHub"
   - Paste the repository URL
   - Choose Python as the language

2. **Set up Firebase Secrets**
   - In your Replit workspace, go to "Tools" > "Secrets"
   - Add the following secrets with your Firebase credentials:
     - `FIREBASE_PROJECT_ID`
     - `FIREBASE_PRIVATE_KEY_ID` 
     - `FIREBASE_PRIVATE_KEY` (include the entire key with BEGIN/END PRIVATE KEY lines)
     - `FIREBASE_CLIENT_EMAIL`
     - `FIREBASE_CLIENT_ID`
     - `FIREBASE_CLIENT_X509_CERT_URL`

3. **Run the App**
   - Click the "Run" button
   - The app should start automatically with the proper Streamlit configuration

## Local Development

### Prerequisites

- Python 3.8+
- Firebase project with Firestore database

### Installation

1. Clone this repository:
   ```bash
   git clone [repository-url]
   cd [repository-directory]
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables for Firebase:
   - Create a `.env` file in the project root
   - Add your Firebase credentials (similar to the Replit Secrets above)

5. Run the application:
   ```bash
   streamlit run app.py
   ```

## Project Structure

- `app.py`: Main Streamlit application
- `data.py`: Data loading and processing functions
- `utils.py`: Utility functions for visualization and analysis
- `firebase_data_loader.py`: Firebase integration functions
- `.streamlit/`: Streamlit configuration
- `requirements.txt`: Python dependencies

## License

[Add license information here]

## Acknowledgements

- Streamlit for the dashboard framework
- Plotly for the visualization libraries
- Firebase for the database 