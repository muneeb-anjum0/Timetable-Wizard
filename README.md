# Timetable Wizard

A web application that automatically scrapes timetable data from Gmail and provides a clean interface for viewing and managing class schedules.

## Project Structure

```
Timetable Wizard/
├── backend/                 # Python Flask backend
│   ├── app.py              # Main Flask application
│   ├── requirements.txt    # Python dependencies
│   ├── database/           # Database modules (Supabase)
│   ├── scraper/            # Email scraping and parsing
│   ├── utils/              # Utility functions
│   ├── credentials/        # Gmail API credentials
│   ├── data/               # Application data and cache
│   ├── logs/               # Application logs
│   └── tests/              # Backend tests
├── frontend/               # React frontend application
│   ├── src/                # React source code
│   ├── public/             # Static assets
│   ├── package.json        # Node.js dependencies
│   └── README.md           # Frontend documentation
├── docs/                   # Project documentation
├── docker-compose.yml      # Development Docker setup
├── docker-compose.prod.yml # Production Docker setup
├── Dockerfile.backend      # Backend Docker configuration
├── Dockerfile.frontend     # Frontend Docker configuration
├── nginx.conf              # Nginx configuration
├── start-dev.bat           # Windows development setup script
├── start-dev.sh            # Unix development setup script
├── run_both.bat            # Windows script to run both services
└── .env                    # Environment variables
```

## Features

- **Automated Email Scraping**: Automatically retrieves timetable data from Gmail
- **Multi-user Support**: Supports multiple users with individual schedules
- **Clean Interface**: Modern React-based web interface
- **Real-time Updates**: Automatic synchronization with email data
- **Responsive Design**: Works on desktop and mobile devices
- **Database Storage**: Uses Supabase for reliable data storage

## Quick Start

### Option 1: Development Setup (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd "Timetable Wizard"
   ```

2. **Run the setup script**
   
   **Windows:**
   ```cmd
   start-dev.bat
   ```
   
   **Linux/Mac:**
   ```bash
   chmod +x start-dev.sh
   ./start-dev.sh
   ```

3. **Configure environment variables**
   - Copy `.env.example` to `.env` (if available)
   - Set up your Gmail API credentials
   - Configure Supabase connection

4. **Start the applications**
   
   **Automatic (Windows):**
   ```cmd
   run_both.bat
   ```
   
   **Manual:**
   ```bash
   # Terminal 1 - Backend
   cd backend
   python app.py
   
   # Terminal 2 - Frontend
   cd frontend
   npm start
   ```

### Option 2: Docker Setup

1. **Development:**
   ```bash
   docker-compose up
   ```

2. **Production:**
   ```bash
   docker-compose -f docker-compose.prod.yml up
   ```

## URLs

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000

## Configuration

### Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# Time zone and schedule settings
TZ=Asia/Karachi
ALLOWED_SEMESTERS=BS (SE) - 5C
CHECK_HOUR_LOCAL=23
CHECK_MINUTE_LOCAL=0
NEWER_THAN_DAYS=2

# Gmail API Configuration
GMAIL_CLIENT_ID=your_gmail_client_id
GMAIL_CLIENT_SECRET=your_gmail_client_secret
GMAIL_QUERY_BASE=subject:("Class Schedule" OR schedule) in:inbox

# Supabase Configuration
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# Debug settings
DEBUG_PARSING=true
```

### Gmail API Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the Gmail API
4. Create credentials (OAuth 2.0 Client ID)
5. Download the credentials and save as `backend/credentials/client_secret.json`

### Supabase Setup

1. Create account at [Supabase](https://supabase.com/)
2. Create a new project
3. Get your project URL and API key
4. Add them to your `.env` file

## Development

### Backend Development

```bash
cd backend
python app.py
```

The Flask development server will run on port 5000 with auto-reload enabled.

### Frontend Development

```bash
cd frontend
npm start
```

The React development server will run on port 3000 with hot reload enabled.

### Testing

```bash
# Backend tests
cd backend
python -m pytest tests/

# Frontend tests
cd frontend
npm test
```

## Deployment

### Docker Deployment

Use the production Docker Compose file:

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Manual Deployment

1. **Backend**: Deploy the Flask app using gunicorn or similar WSGI server
2. **Frontend**: Build and serve the React app using nginx or similar web server

## API Documentation

The backend provides RESTful API endpoints:

- `GET /api/health` - Health check
- `GET /api/timetable` - Get timetable data
- `POST /api/scrape` - Trigger manual scrape
- `GET /api/status` - Get scraper status
- And more...

See `backend/app.py` for the complete API documentation.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

[Add your license information here]

## Support

For issues and questions, please create an issue in the repository or contact the development team.