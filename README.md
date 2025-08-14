# CityGuard AI - Local Incident Monitoring System

CityGuard AI is a comprehensive real-time local incident monitoring and alert system that aggregates data from multiple sources, uses AI-powered analysis to assess incident relevance and severity, and delivers targeted notifications to keep residents informed about critical safety information.

![CityGuard AI](https://img.shields.io/badge/Status-Active-brightgreen) ![Python](https://img.shields.io/badge/Python-3.11+-blue) ![Flask](https://img.shields.io/badge/Flask-Latest-lightgrey) ![AI](https://img.shields.io/badge/AI-Gemini%202.5-orange)

## ✨ Key Features

### 🎯 Multi-Agent Architecture
- **Data Agent**: Automatically fetches incident data from weather and news APIs every 10 minutes
- **Notification Agent**: Processes incidents using Google's Gemini AI for intelligent analysis and user notifications
- **Background Processing**: APScheduler handles continuous monitoring without manual intervention

### 🌐 Comprehensive Web Interface
- **Main Dashboard**: Overview of all incidents with real-time filtering and statistics
- **Weather Alerts Page**: Specialized weather monitoring with severity-based filtering
- **News Alerts Page**: Local news incident tracking with breaking news ticker
- **Interactive Map**: Geographic visualization of incidents using Leaflet.js
- **Subscription Management**: Email alert registration for high-priority incidents

### 🤖 AI-Powered Analysis
- **Relevance Scoring**: Gemini AI evaluates incident relevance to local communities (0-1 score)
- **Severity Assessment**: Automatic classification into Critical, High, Medium, and Low priority levels
- **Content Summarization**: AI-generated summaries for better incident understanding
- **Credibility Verification**: Filters out unreliable information to prevent misinformation

### 📡 Real-Time Data Sources
- **OpenWeatherMap API**: Severe weather alerts and meteorological warnings
- **News API**: Local news aggregation for incident discovery
- **Multi-Location Support**: Configurable monitoring for different geographic areas

## 🚀 Quick Start

### Prerequisites
- Python 3.11 or higher
- Valid API keys for:
  - Google Gemini API (`GEMINI_API_KEY`)
  - OpenWeatherMap API (`OPENWEATHERMAP_API_KEY`)
  - News API (`NEWS_API_KEY`)

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/AishwaryaChandel27/CityGuardAlert
   cd cityguard-ai
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set environment variables:
   ```bash
   export GEMINI_API_KEY="your_gemini_api_key"
   export OPENWEATHERMAP_API_KEY="your_openweathermap_key"
   export NEWS_API_KEY="your_news_api_key"
   export SESSION_SECRET="your_session_secret"
   ```

4. Run the application:
   ```bash
   python main.py
   ```

5. Access the web interface at `http://localhost:5000`

## 📊 System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Data Agent    │    │ Notification     │    │   Web Interface │
│                 │    │     Agent        │    │                 │
│ • Weather API   │───▶│                  │───▶│ • Dashboard     │
│ • News API      │    │ • Gemini AI      │    │ • Weather Page  │
│ • Scheduled     │    │ • Analysis       │    │ • News Page     │
│   Fetching      │    │ • Email Alerts   │    │ • Interactive   │
└─────────────────┘    └──────────────────┘    │   Map           │
                                                └─────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │    Database      │
                    │                  │
                    │ • Incidents      │
                    │ • Users          │
                    │ • Subscriptions  │
                    │ • Notifications  │
                    └──────────────────┘
```

## 📱 Web Interface Overview

### Dashboard (`/`)
- **Real-time Statistics**: Live incident counters and severity breakdown
- **Incident Timeline**: Chronological list of all recent incidents
- **Advanced Filtering**: Filter by source, severity, location, and time range
- **Quick Actions**: Easy access to detailed views and external sources

### Weather Alerts (`/weather`)
- **Weather-Specific Dashboard**: Dedicated interface for meteorological events
- **Severity Indicators**: Visual severity classification (Critical → Low)
- **Weather Type Filtering**: Filter by storm, rain, snow, fog, wind conditions
- **Current Conditions**: Real-time weather status display

### News Alerts (`/news`)
- **Local News Monitoring**: Curated local incident reporting
- **Breaking News Ticker**: Highlights for critical incidents
- **Category Classification**: Emergency, Traffic, Crime, Infrastructure, Health
- **Source Verification**: Direct links to original news articles

### Interactive Map (`/map`)
- **Geographic Visualization**: Leaflet.js-powered incident mapping
- **Location-Based Filtering**: Focus on specific areas or search locations
- **Severity Color Coding**: Visual severity representation with custom markers
- **Real-Time Updates**: Live incident location tracking

### Subscription Management (`/subscribe`)
- **Email Alert Registration**: User subscription for critical incidents
- **Preference Settings**: Customizable alert thresholds and categories
- **Instant Notifications**: Immediate email alerts for high-priority events

## 🔧 API Endpoints

### Public Endpoints
- `GET /api/incidents` - Retrieve all incidents with filtering options
- `GET /api/incidents/weather` - Weather-specific incidents
- `GET /api/incidents/news` - News-specific incidents
- `GET /api/incidents/<id>` - Individual incident details

### Query Parameters
- `hours` - Time range filter (default: 24)
- `min_relevance` - Minimum relevance score (default: 0.3)
- `source` - Filter by data source (weather/news)
- `severity` - Filter by severity level

### Response Format
```json
{
  "success": true,
  "incidents": [
    {
      "id": 1,
      "title": "Weather Alert: Fog",
      "description": "Dense fog conditions affecting visibility",
      "ai_summary": "Fog reported in New York, exercise caution while traveling",
      "severity": "low",
      "category": "weather",
      "source": "weather",
      "location": "New York",
      "relevance_score": 0.5,
      "is_verified": true,
      "created_at": "2025-08-14T10:30:00Z",
      "url": null
    }
  ],
  "count": 1
}
```

## 🗃️ Database Schema

### Incidents Table
- `id` - Primary key
- `title` - Incident title
- `description` - Original incident description
- `ai_summary` - AI-generated summary
- `severity` - Severity level (low/medium/high/critical)
- `category` - Incident category
- `source` - Data source (weather/news)
- `location` - Geographic location
- `relevance_score` - AI relevance score (0.0-1.0)
- `is_verified` - AI verification status
- `url` - Source URL (for news incidents)
- `created_at` - Timestamp

### Users Table
- `id` - Primary key
- `username` - Unique username
- `email` - Email address
- `password_hash` - Encrypted password

### Alert Subscriptions Table
- `id` - Primary key
- `user_id` - Foreign key to Users
- `severity_threshold` - Minimum severity for alerts
- `categories` - Subscribed incident categories
- `is_active` - Subscription status

## 🔮 AI Analysis Pipeline

### 1. Data Ingestion
```python
# Weather data from OpenWeatherMap
weather_data = weather_api.get_current_conditions()
weather_alerts = weather_api.get_alerts()

# News data from NewsAPI
news_articles = news_api.search_local_incidents()
```

### 2. AI Processing
```python
# Gemini AI analysis for each incident
analysis = gemini.analyze_incident({
    "title": incident.title,
    "description": incident.description,
    "location": incident.location
})

# Returns structured analysis
{
    "relevance_score": 0.75,
    "severity": "high",
    "category": "weather",
    "is_credible": true,
    "summary": "AI-generated incident summary"
}
```

### 3. Notification Logic
```python
# Email notifications for high-priority incidents
if incident.severity in ['critical', 'high'] and incident.relevance_score > 0.7:
    notification_agent.send_email_alerts(incident, subscribers)
```

## ⚙️ Configuration

### Environment Variables
```bash
# Required API Keys
GEMINI_API_KEY=your_gemini_api_key_here
OPENWEATHERMAP_API_KEY=your_openweather_api_key
NEWS_API_KEY=your_news_api_key

# Application Settings
SESSION_SECRET=your_secure_session_secret
DATABASE_URL=sqlite:///instance/cityguard.db  # Local development
DATABASE_URL=postgresql://user:pass@host/db   # Production

# Email Configuration (Optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USER=your_email@gmail.com
EMAIL_PASS=your_app_password
```

### Monitoring Settings
```python
# Data Agent Configuration
WEATHER_FETCH_INTERVAL = 10  # minutes
NEWS_FETCH_INTERVAL = 10     # minutes
MAX_INCIDENTS_PER_FETCH = 5

# AI Analysis Thresholds
MIN_RELEVANCE_SCORE = 0.3
HIGH_PRIORITY_THRESHOLD = 0.7
CRITICAL_ALERT_THRESHOLD = 0.9
```

## 📈 Performance & Scalability

### Optimizations
- **Database Indexing**: Optimized queries on frequently accessed fields
- **Background Processing**: Non-blocking API calls using APScheduler
- **Caching**: Frontend caching for improved user experience
- **Rate Limiting**: API request throttling to respect service limits

### Production Deployment
- **Database**: PostgreSQL recommended for production
- **Web Server**: Gunicorn with multiple workers
- **Reverse Proxy**: Nginx for static file serving and load balancing
- **Monitoring**: Application logging and error tracking
- **SSL/TLS**: HTTPS encryption for secure communication

## 🛠️ Development

### Project Structure
```
cityguard-ai/
├── agents/
│   ├── data_agent.py          # Data fetching automation
│   └── notification_agent.py  # AI processing and alerts
├── templates/
│   ├── base.html             # Base template with navigation
│   ├── index.html            # Main dashboard
│   ├── weather.html          # Weather alerts page
│   ├── news.html             # News alerts page
│   ├── map.html              # Interactive map
│   └── subscribe.html        # Subscription management
├── static/
│   ├── css/custom.css        # Custom styling
│   └── js/dashboard.js       # Frontend JavaScript
├── utils/
│   └── email_service.py      # Email notification utilities
├── app.py                    # Flask application factory
├── main.py                   # Application entry point
├── models.py                 # Database models
├── routes.py                 # Web routes and API endpoints
├── gemini.py                 # Gemini AI integration
└── README.md                 # This file
```

### Testing
```bash
# Run the application in debug mode
export FLASK_ENV=development
python main.py

# Check API endpoints
curl http://localhost:5000/api/incidents
curl http://localhost:5000/api/incidents/weather?hours=12
```

### Contributing
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Make changes and test thoroughly
4. Commit changes (`git commit -am 'Add new feature'`)
5. Push to branch (`git push origin feature/new-feature`)
6. Create Pull Request

## 📄 License

This project is licensed under the MIT License. See LICENSE file for details.

## 🤝 Support

For support, feature requests, or bug reports:
- Create an issue in the repository
- Contact the development team
- Check the documentation for troubleshooting guides

## 🔄 Recent Updates

**Version 2.0.0** (August 2025)
- Added dedicated weather alerts page with specialized filtering
- Implemented news alerts page with breaking news ticker
- Integrated interactive map with Leaflet.js for geographic visualization
- Enhanced navigation with separate pages for different data types
- Improved AI analysis with structured incident categorization
- Added real-time statistics and enhanced filtering options

---

**CityGuard AI** - Keeping communities safe through intelligent incident monitoring.
