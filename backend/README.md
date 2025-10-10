# Backend

This directory contains all the backend code for the Timetable Wizard application.

## Structure

```
backend/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── credentials/          # Gmail API credentials
├── data/                # Application data and cache
├── logs/                # Application logs
├── tests/               # Backend tests
├── database/            # Database modules (Supabase)
├── scraper/             # Email scraping and parsing modules
└── utils/               # Utility modules
```

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the Flask application:
   ```bash
   python app.py
   ```

The backend API will be available at `http://localhost:5000`.

## Environment Variables

Make sure to set up the required environment variables in the `.env` file at the project root:

- `SUPABASE_URL`
- `SUPABASE_KEY`
- `GMAIL_CLIENT_ID`
- `GMAIL_CLIENT_SECRET`
- Other configuration variables as needed

## API Endpoints

The backend provides RESTful API endpoints for the frontend application. See `app.py` for the complete list of available endpoints.