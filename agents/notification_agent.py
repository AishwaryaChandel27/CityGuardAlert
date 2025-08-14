import logging
from datetime import datetime, timedelta
from app import db
from models import Incident, User, AlertSubscription, NotificationLog
from gemini import analyze_incident, filter_credible_sources
from utils.email_service import EmailService

class NotificationAgent:
    def __init__(self):
        self.email_service = EmailService()
        
    def process_incidents(self, incident_data_list):
        """Process new incidents with AI analysis and send notifications"""
        logging.info(f"Notification Agent: Processing {len(incident_data_list)} incidents")
        
        processed_incidents = []
        
        for incident_data in incident_data_list:
            try:
                # Use Gemini AI to analyze the incident
                analysis = analyze_incident(
                    title=incident_data['title'],
                    description=incident_data['description'],
                    source=incident_data['source'],
                    location=incident_data['location']
                )
                
                # Additional credibility check
                is_credible = filter_credible_sources(
                    content=incident_data['description'],
                    source_url=incident_data.get('url', '')
                )
                
                # Override AI decision if our filter disagrees
                if not is_credible:
                    analysis.is_credible = False
                    analysis.relevance_score *= 0.5  # Reduce relevance for non-credible sources
                
                # Only process incidents that meet minimum criteria
                if analysis.relevance_score >= 0.3 and analysis.is_credible:
                    # Save to database
                    incident = self.save_analyzed_incident(incident_data, analysis)
                    if incident:
                        processed_incidents.append(incident)
                        
                        # Send notifications for high-priority incidents
                        if analysis.severity in ['high', 'critical'] and analysis.relevance_score >= 0.7:
                            self.send_notifications(incident)
                
            except Exception as e:
                logging.error(f"Notification Agent: Error processing incident {incident_data.get('title', '')}: {e}")
        
        logging.info(f"Notification Agent: Successfully processed {len(processed_incidents)} incidents")
        return processed_incidents
    
    def save_analyzed_incident(self, incident_data, analysis):
        """Save incident with AI analysis to database"""
        try:
            # Check for existing incident to avoid duplicates
            existing = Incident.query.filter_by(
                title=incident_data['title'],
                source=incident_data['source']
            ).filter(
                Incident.created_at >= datetime.utcnow() - timedelta(hours=24)
            ).first()
            
            if existing:
                # Update existing incident with new analysis
                existing.ai_summary = analysis.summary
                existing.relevance_score = analysis.relevance_score
                existing.severity = analysis.severity
                existing.category = analysis.category
                existing.is_verified = analysis.is_credible
                existing.updated_at = datetime.utcnow()
                incident = existing
            else:
                # Create new incident
                incident = Incident(
                    title=incident_data['title'],
                    description=incident_data['description'],
                    source=incident_data['source'],
                    location=incident_data['location'],
                    category=analysis.category,
                    severity=analysis.severity,
                    url=incident_data.get('url'),
                    raw_data=incident_data.get('raw_data'),
                    ai_summary=analysis.summary,
                    relevance_score=analysis.relevance_score,
                    is_verified=analysis.is_credible
                )
                db.session.add(incident)
            
            db.session.commit()
            logging.debug(f"Notification Agent: Saved incident {incident.id}: {incident.title}")
            return incident
            
        except Exception as e:
            logging.error(f"Notification Agent: Failed to save incident: {e}")
            db.session.rollback()
            return None
    
    def send_notifications(self, incident):
        """Send notifications to subscribed users for high-priority incidents"""
        try:
            # Get users who should receive this notification
            eligible_users = self.get_eligible_users(incident)
            
            for user in eligible_users:
                try:
                    if user.email_notifications:
                        # Send email notification
                        success = self.email_service.send_alert_email(user, incident)
                        
                        # Log notification attempt
                        log_entry = NotificationLog(
                            incident_id=incident.id,
                            user_id=user.id,
                            notification_type='email',
                            status='sent' if success else 'failed',
                            error_message=None if success else 'Email sending failed'
                        )
                        db.session.add(log_entry)
                
                except Exception as e:
                    logging.error(f"Notification Agent: Failed to send notification to user {user.id}: {e}")
                    
                    # Log failed notification
                    log_entry = NotificationLog(
                        incident_id=incident.id,
                        user_id=user.id,
                        notification_type='email',
                        status='failed',
                        error_message=str(e)
                    )
                    db.session.add(log_entry)
            
            db.session.commit()
            logging.info(f"Notification Agent: Sent notifications for incident {incident.id} to {len(eligible_users)} users")
            
        except Exception as e:
            logging.error(f"Notification Agent: Error sending notifications for incident {incident.id}: {e}")
            db.session.rollback()
    
    def get_eligible_users(self, incident):
        """Get users who should receive notifications for this incident"""
        try:
            # Get users with active subscriptions matching this incident
            eligible_users = []
            
            # Simple matching for now - can be enhanced with more sophisticated location/category matching
            users = User.query.filter_by(email_notifications=True).all()
            
            for user in users:
                # Check if user's location matches (simple string matching)
                if user.location.lower() in incident.location.lower() or incident.location.lower() in user.location.lower():
                    # Check severity threshold (assuming users want medium+ severity by default)
                    severity_levels = {'low': 1, 'medium': 2, 'high': 3, 'critical': 4}
                    incident_severity_level = severity_levels.get(incident.severity, 2)
                    
                    if incident_severity_level >= 2:  # medium or higher
                        eligible_users.append(user)
            
            return eligible_users
            
        except Exception as e:
            logging.error(f"Notification Agent: Error finding eligible users: {e}")
            return []
    
    def get_recent_incidents(self, hours=24, min_relevance=0.3):
        """Get recent incidents for dashboard display"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            incidents = Incident.query.filter(
                Incident.created_at >= cutoff_time,
                Incident.relevance_score >= min_relevance,
                Incident.is_verified == True
            ).order_by(
                Incident.relevance_score.desc(),
                Incident.created_at.desc()
            ).limit(20).all()
            
            return incidents
            
        except Exception as e:
            logging.error(f"Notification Agent: Error fetching recent incidents: {e}")
            return []
