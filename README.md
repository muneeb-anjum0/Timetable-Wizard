# Timetable Wizard

A smart automation solution that solves the daily struggle of manually searching through emails for university timetables. Built specifically for SZABIST University students who receive daily schedule updates via email.

## The Problem I Solved

Every day at SZABIST University, students receive their class timetables through email. Finding today's schedule meant digging through countless emails, scrolling through lengthy content, and manually parsing the information. This repetitive task was eating up precious time that could be better spent on actual studies.

## How It Works

Timetable Wizard automates the entire process by:

- **Gmail Integration**: Connects to your Gmail account using Google's OAuth API to securely access your emails
- **Smart Email Parsing**: Searches for emails containing timetable information using intelligent keyword matching
- **HTML Content Extraction**: Parses complex email HTML content to extract structured schedule data
- **Multi-User Support**: Each user gets their own personalized dashboard with isolated data
- **Semester Filtering**: Configurable filters to show only relevant courses for your specific semester
- **Real-time Updates**: Automatic scraping with scheduler that checks for new timetables

## Technology Stack

### Backend (Python/Flask)
- **Flask API**: RESTful endpoints serving the React frontend
- **Gmail API**: Official Google API integration for secure email access
- **BeautifulSoup**: HTML parsing and content extraction
- **APScheduler**: Automated daily scraping functionality
- **Supabase**: PostgreSQL database for multi-user data management
- **Rich**: Enhanced terminal UI for debugging and monitoring

### Frontend (React/TypeScript)
- **React 19**: Modern UI with TypeScript for type safety
- **Tailwind CSS**: Responsive and clean interface design
- **Framer Motion**: Smooth animations and transitions
- **Axios**: API communication with the Flask backend
- **Context API**: State management for authentication and data

### Database Design

The system uses Supabase (PostgreSQL) with a clean multi-tenant architecture:

- **Users Table**: Stores user authentication and profile information
- **Tokens Table**: Securely manages Gmail OAuth tokens for each user
- **Timetable Cache**: Stores parsed schedule data with automatic cleanup
- **Audit Logs**: Tracks scraping activities and system health

Key design decisions:
- User isolation ensures data privacy between different accounts
- Token encryption for secure Gmail access
- Automatic cache expiration to keep data fresh
- Optimized queries for fast frontend loading

## Features That Make Life Easier

### Smart Parsing Engine
- Handles multiple email formats and layouts
- Robust error handling for malformed content
- Intelligent semester detection and filtering
- Course title corrections and data validation

### User Experience
- One-click Gmail authentication
- Clean tabular display of schedule data
- Real-time status updates during scraping
- Responsive design for mobile and desktop
- Semester management for filtering relevant courses

### Developer Experience
- Comprehensive logging and error tracking
- Health check endpoints for monitoring
- Environment-based configuration
- Docker support for easy deployment
- Extensive error handling and recovery

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- Gmail account with API access enabled
- Supabase account for database

### Setup
1. **Clone the repository**
   ```bash
   git clone https://github.com/muneeb-anjum0/Timetable-Wizard.git
   cd Timetable-Wizard
   ```

2. **Backend Setup**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Environment Configuration**
   Create `.env` file with:
   ```
   SUPABASE_URL=your_supabase_url
   SUPABASE_SERVICE_KEY=your_service_key
   ALLOWED_SEMESTERS=BS (SE) - 5C, BS (CS) - 7A
   ```

4. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm start
   ```

5. **Google OAuth Setup**
   - Create Google Cloud project
   - Enable Gmail API
   - Download client credentials to `backend/credentials/client_secret.json`

## Architecture Highlights

### Security First
- OAuth 2.0 authentication flow
- Encrypted token storage
- CORS configuration for secure API access
- Input validation and sanitization

### Scalability
- Multi-user architecture from day one
- Database optimization for concurrent users
- Caching layers for improved performance
- Modular design for easy feature additions

### Reliability
- Comprehensive error handling and recovery
- Automatic retry mechanisms for API calls
- Graceful degradation when services are unavailable
- Extensive logging for debugging and monitoring

## Impact

This project transforms a daily 10-15 minute manual task into a seamless automated experience. Students can now focus on their studies instead of hunting through emails for their class schedules. The clean interface and reliable automation have made schedule management effortless for SZABIST University students.

## Going Live Soon

The application is currently in final testing phase and will be deployed for public use once a few remaining bugs are resolved. Stay tuned for the live deployment announcement!

## Future Enhancements

- Mobile app development
- Calendar integration (Google Calendar, Outlook)
- WhatsApp/SMS notifications for schedule changes
- Analytics dashboard for attendance tracking
- Integration with university's official systems

---

Built with passion to solve real student problems and make university life a little bit easier.