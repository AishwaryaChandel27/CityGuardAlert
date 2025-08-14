from flask import render_template, request, jsonify, redirect, url_for, flash
from app import app, db
from models import User, Incident, AlertSubscription
from agents.notification_agent import NotificationAgent
from werkzeug.security import generate_password_hash, check_password_hash
import logging

notification_agent = NotificationAgent()

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/api/incidents')
def get_incidents():
    """API endpoint to get recent incidents for dashboard"""
    try:
        hours = request.args.get('hours', 24, type=int)
        min_relevance = request.args.get('min_relevance', 0.3, type=float)
        
        incidents = notification_agent.get_recent_incidents(hours=hours, min_relevance=min_relevance)
        
        incidents_data = []
        for incident in incidents:
            incidents_data.append(incident.to_dict())
        
        return jsonify({
            'success': True,
            'incidents': incidents_data,
            'count': len(incidents_data)
        })
        
    except Exception as e:
        logging.error(f"Error fetching incidents: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch incidents',
            'incidents': [],
            'count': 0
        }), 500

@app.route('/api/incidents/<int:incident_id>')
def get_incident_details(incident_id):
    """Get detailed information about a specific incident"""
    try:
        incident = Incident.query.get_or_404(incident_id)
        return jsonify({
            'success': True,
            'incident': incident.to_dict()
        })
        
    except Exception as e:
        logging.error(f"Error fetching incident {incident_id}: {e}")
        return jsonify({
            'success': False,
            'error': 'Incident not found'
        }), 404

@app.route('/api/incidents/by-severity/<severity>')
def get_incidents_by_severity(severity):
    """Get incidents filtered by severity level"""
    try:
        valid_severities = ['low', 'medium', 'high', 'critical']
        if severity not in valid_severities:
            return jsonify({
                'success': False,
                'error': 'Invalid severity level'
            }), 400
        
        incidents = Incident.query.filter_by(
            severity=severity,
            is_verified=True
        ).order_by(
            Incident.created_at.desc()
        ).limit(10).all()
        
        incidents_data = [incident.to_dict() for incident in incidents]
        
        return jsonify({
            'success': True,
            'incidents': incidents_data,
            'severity': severity,
            'count': len(incidents_data)
        })
        
    except Exception as e:
        logging.error(f"Error fetching incidents by severity {severity}: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch incidents'
        }), 500

@app.route('/subscribe', methods=['GET', 'POST'])
def subscribe():
    """Handle user subscription for email notifications"""
    if request.method == 'POST':
        try:
            email = request.form.get('email', '').strip()
            location = request.form.get('location', '').strip()
            username = request.form.get('username', '').strip()
            
            if not email or not location or not username:
                flash('Please fill in all required fields.', 'error')
                return redirect(url_for('subscribe'))
            
            # Check if user already exists
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                flash('Email already subscribed to notifications.', 'info')
                return redirect(url_for('index'))
            
            # Create new user subscription
            user = User(
                username=username,
                email=email,
                location=location,
                email_notifications=True
            )
            
            db.session.add(user)
            db.session.commit()
            
            flash('Successfully subscribed to CityGuard AI notifications!', 'success')
            return redirect(url_for('index'))
            
        except Exception as e:
            logging.error(f"Error creating subscription: {e}")
            db.session.rollback()
            flash('Error creating subscription. Please try again.', 'error')
            return redirect(url_for('subscribe'))
    
    return render_template('subscribe.html')

@app.route('/api/stats')
def get_stats():
    """Get dashboard statistics"""
    try:
        from datetime import datetime, timedelta
        
        # Get counts for the last 24 hours
        last_24h = datetime.utcnow() - timedelta(hours=24)
        
        total_incidents = Incident.query.filter(
            Incident.created_at >= last_24h,
            Incident.is_verified == True
        ).count()
        
        critical_incidents = Incident.query.filter(
            Incident.created_at >= last_24h,
            Incident.severity == 'critical',
            Incident.is_verified == True
        ).count()
        
        high_incidents = Incident.query.filter(
            Incident.created_at >= last_24h,
            Incident.severity == 'high',
            Incident.is_verified == True
        ).count()
        
        weather_incidents = Incident.query.filter(
            Incident.created_at >= last_24h,
            Incident.source == 'weather',
            Incident.is_verified == True
        ).count()
        
        news_incidents = Incident.query.filter(
            Incident.created_at >= last_24h,
            Incident.source == 'news',
            Incident.is_verified == True
        ).count()
        
        active_users = User.query.filter_by(email_notifications=True).count()
        
        return jsonify({
            'success': True,
            'stats': {
                'total_incidents_24h': total_incidents,
                'critical_incidents_24h': critical_incidents,
                'high_incidents_24h': high_incidents,
                'weather_incidents_24h': weather_incidents,
                'news_incidents_24h': news_incidents,
                'active_subscribers': active_users,
                'last_updated': datetime.utcnow().isoformat()
            }
        })
        
    except Exception as e:
        logging.error(f"Error fetching stats: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch statistics'
        }), 500

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    logging.error(f"Internal server error: {e}")
    return render_template('500.html'), 500
