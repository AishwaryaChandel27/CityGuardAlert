import logging
import requests
import os
import json
from datetime import datetime
from app import db
from models import Incident
from agents.notification_agent import NotificationAgent

class DataAgent:
    def __init__(self):
        self.weather_api_key = os.environ.get("OPENWEATHERMAP_API_KEY", "default_weather_key")
        self.news_api_key = os.environ.get("NEWS_API_KEY", "default_news_key")
        self.default_location = os.environ.get("DEFAULT_LOCATION", "New York")
        self.notification_agent = None
        
    def fetch_all_data(self):
        """Fetch data from all sources and trigger notification processing"""
        logging.info("Data Agent: Starting data fetch cycle")
        
        try:
            weather_incidents = self.fetch_weather_data()
            news_incidents = self.fetch_news_data()
            
            all_incidents = weather_incidents + news_incidents
            logging.info(f"Data Agent: Fetched {len(all_incidents)} total incidents")
            
            # Trigger notification agent to process new incidents
            if all_incidents and not self.notification_agent:
                self.notification_agent = NotificationAgent()
            
            if all_incidents and self.notification_agent:
                self.notification_agent.process_incidents(all_incidents)
                
        except Exception as e:
            logging.error(f"Data Agent: Error in fetch cycle: {e}")
    
    def fetch_weather_data(self):
        """Fetch weather alerts and warnings from OpenWeatherMap API"""
        incidents = []
        
        try:
            # Get current weather alerts
            url = f"http://api.openweathermap.org/data/2.5/weather"
            params = {
                'q': self.default_location,
                'appid': self.weather_api_key,
                'units': 'metric'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            weather_data = response.json()
            
            # Check for severe weather conditions
            if 'weather' in weather_data:
                for weather in weather_data['weather']:
                    main = weather.get('main', '').lower()
                    description = weather.get('description', '')
                    
                    # Check for severe weather conditions
                    severe_conditions = ['thunderstorm', 'snow', 'rain', 'drizzle', 'mist', 'fog']
                    if any(condition in main for condition in severe_conditions):
                        incident_data = {
                            'title': f"Weather Alert: {weather.get('main', 'Unknown')}",
                            'description': f"Current weather conditions: {description}. Temperature: {weather_data.get('main', {}).get('temp', 'N/A')}°C",
                            'source': 'weather',
                            'location': self.default_location,
                            'category': 'weather',
                            'raw_data': json.dumps(weather_data),
                            'url': f"https://openweathermap.org/city/{weather_data.get('id', '')}"
                        }
                        incidents.append(incident_data)
            
            # Also fetch weather alerts if available
            alerts_url = f"http://api.openweathermap.org/data/2.5/onecall"
            
            # Get coordinates first
            if 'coord' in weather_data:
                lat = weather_data['coord']['lat']
                lon = weather_data['coord']['lon']
                
                alerts_params = {
                    'lat': lat,
                    'lon': lon,
                    'appid': self.weather_api_key,
                    'exclude': 'minutely,hourly,daily'
                }
                
                alerts_response = requests.get(alerts_url, params=alerts_params, timeout=10)
                if alerts_response.status_code == 200:
                    alerts_data = alerts_response.json()
                    
                    if 'alerts' in alerts_data:
                        for alert in alerts_data['alerts']:
                            incident_data = {
                                'title': f"Weather Alert: {alert.get('event', 'Weather Warning')}",
                                'description': alert.get('description', 'Weather alert issued for your area'),
                                'source': 'weather',
                                'location': self.default_location,
                                'category': 'weather',
                                'raw_data': json.dumps(alert),
                                'url': 'https://openweathermap.org'
                            }
                            incidents.append(incident_data)
            
            logging.info(f"Data Agent: Fetched {len(incidents)} weather incidents")
            
        except requests.exceptions.RequestException as e:
            logging.error(f"Data Agent: Weather API request failed: {e}")
        except Exception as e:
            logging.error(f"Data Agent: Weather data processing failed: {e}")
        
        return incidents
    
    def fetch_news_data(self):
        """Fetch local news incidents from NewsAPI"""
        incidents = []
        
        try:
            # Search for local incidents and emergencies
            keywords = ['accident', 'emergency', 'police', 'fire', 'traffic', 'closure', 'incident', 'alert', 'warning']
            
            for keyword in keywords[:3]:  # Limit to avoid rate limits
                url = "https://newsapi.org/v2/everything"
                params = {
                    'q': f'{keyword} AND {self.default_location}',
                    'apiKey': self.news_api_key,
                    'language': 'en',
                    'sortBy': 'publishedAt',
                    'pageSize': 5,
                    'from': datetime.now().strftime('%Y-%m-%d')
                }
                
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                news_data = response.json()
                
                if 'articles' in news_data:
                    for article in news_data['articles']:
                        # Skip articles without proper content
                        if not article.get('title') or not article.get('description'):
                            continue
                            
                        # Skip removed articles
                        if '[Removed]' in str(article.get('title', '')):
                            continue
                        
                        incident_data = {
                            'title': article.get('title', 'News Alert'),
                            'description': article.get('description', 'Local news incident reported'),
                            'source': 'news',
                            'location': self.default_location,
                            'category': 'other',  # Will be determined by AI
                            'url': article.get('url', ''),
                            'raw_data': json.dumps(article)
                        }
                        incidents.append(incident_data)
            
            logging.info(f"Data Agent: Fetched {len(incidents)} news incidents")
            
        except requests.exceptions.RequestException as e:
            logging.error(f"Data Agent: News API request failed: {e}")
        except Exception as e:
            logging.error(f"Data Agent: News data processing failed: {e}")
        
        return incidents
    
    def save_incident(self, incident_data, analysis=None):
        """Save incident to database with optional AI analysis"""
        try:
            # Check if incident already exists (avoid duplicates)
            existing = Incident.query.filter_by(
                title=incident_data['title'],
                source=incident_data['source']
            ).first()
            
            if existing:
                # Update existing incident
                existing.updated_at = datetime.utcnow()
                if analysis:
                    existing.ai_summary = analysis.summary
                    existing.relevance_score = analysis.relevance_score
                    existing.severity = analysis.severity
                    existing.category = analysis.category
                    existing.is_verified = analysis.is_credible
            else:
                # Create new incident
                incident = Incident(
                    title=incident_data['title'],
                    description=incident_data['description'],
                    source=incident_data['source'],
                    location=incident_data['location'],
                    category=incident_data.get('category', 'other'),
                    url=incident_data.get('url'),
                    raw_data=incident_data.get('raw_data')
                )
                
                if analysis:
                    incident.ai_summary = analysis.summary
                    incident.relevance_score = analysis.relevance_score
                    incident.severity = analysis.severity
                    incident.category = analysis.category
                    incident.is_verified = analysis.is_credible
                
                db.session.add(incident)
            
            db.session.commit()
            logging.debug(f"Data Agent: Saved incident: {incident_data['title']}")
            
        except Exception as e:
            logging.error(f"Data Agent: Failed to save incident: {e}")
            db.session.rollback()
