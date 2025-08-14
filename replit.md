# Overview

CityGuard AI is a local incident monitoring and alert system that aggregates real-time data from multiple sources (weather APIs and news APIs) to provide residents with critical safety information. The system uses AI-powered analysis through Google's Gemini API to assess incident relevance, severity, and credibility before sending targeted notifications to subscribers. It features a live dashboard for monitoring incidents, user subscription management, and automated email alerts for high-priority events.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
The application uses a traditional server-rendered architecture with Flask templates and Bootstrap for styling. The frontend consists of:
- **Template System**: Jinja2 templates with a base layout (`base.html`) providing consistent navigation and styling
- **Dashboard Interface**: Real-time incident display with JavaScript-powered updates and filtering
- **Bootstrap Integration**: Uses Replit's dark theme variant for consistent UI styling
- **Progressive Enhancement**: JavaScript enhances the base HTML functionality without being required for core features

## Backend Architecture
Built on Flask with a modular agent-based architecture:
- **Flask Application**: Central application factory pattern with SQLAlchemy ORM integration
- **Agent Pattern**: Separate agents handle distinct responsibilities:
  - `DataAgent`: Fetches incident data from external APIs (weather and news)
  - `NotificationAgent`: Processes incidents through AI analysis and manages user notifications
- **Database Layer**: SQLAlchemy models with relationships between Users, Incidents, and AlertSubscriptions
- **Background Processing**: APScheduler handles periodic data fetching and processing tasks

## AI Integration
The system leverages Google's Gemini API for intelligent incident analysis:
- **Incident Analysis**: Structured assessment of relevance score, severity level, category classification, and credibility verification
- **Content Filtering**: Additional credibility checks to prevent misinformation propagation
- **Automated Categorization**: Classifies incidents into predefined categories (weather, traffic, crime, emergency, etc.)

## Data Storage
Uses SQLAlchemy with configurable database backends:
- **Development**: SQLite for local development and testing
- **Production**: PostgreSQL support via DATABASE_URL environment variable
- **Schema Design**: Normalized structure with Users, Incidents, AlertSubscriptions, and NotificationLog tables
- **Data Retention**: Timestamps on all entities for historical tracking and cleanup

## Authentication and Authorization
Simple authentication system using Flask-Login:
- **User Management**: Username/email registration with password hashing
- **Session Management**: Flask sessions with configurable secret keys
- **No Complex Roles**: Single user role with subscription-based access control

# External Dependencies

## Core APIs
- **Google Gemini API**: AI-powered incident analysis and content verification
- **OpenWeatherMap API**: Real-time weather alerts and severe weather warnings
- **News API**: News article aggregation for incident discovery

## Email Services
- **SMTP Integration**: Configurable email service for alert notifications
- **Gmail Support**: Default SMTP configuration for Gmail with app password authentication

## Frontend Libraries
- **Bootstrap 5**: UI framework with Replit's dark theme integration
- **Feather Icons**: Icon system for consistent visual elements
- **Vanilla JavaScript**: No heavy frontend frameworks, using fetch API for AJAX calls

## Infrastructure
- **Flask Ecosystem**: Core web framework with extensions for CORS, SQLAlchemy, and Login management
- **APScheduler**: Background task scheduling for periodic data fetching
- **ProxyFix**: Middleware for handling reverse proxy headers in deployment

## Development Tools
- **Werkzeug**: Development server and debugging utilities
- **Python Logging**: Comprehensive logging throughout the application stack