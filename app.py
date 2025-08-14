import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import atexit

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Enable CORS for API endpoints
CORS(app)

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///cityguard.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize the app with the extension
db.init_app(app)

# Initialize scheduler
scheduler = BackgroundScheduler()
scheduler.start()

with app.app_context():
    # Import models to ensure tables are created
    import models  # noqa: F401
    db.create_all()
    
    # Import and register routes
    import routes  # noqa: F401
    
    # Import agents and start background tasks
    from agents.data_agent import DataAgent
    from agents.notification_agent import NotificationAgent
    
    # Initialize agents
    data_agent = DataAgent()
    notification_agent = NotificationAgent()
    
    # Schedule data fetching every 10 minutes
    scheduler.add_job(
        func=data_agent.fetch_all_data,
        trigger=IntervalTrigger(minutes=10),
        id='fetch_data_job',
        name='Fetch weather and news data',
        replace_existing=True
    )
    
    # Initial data fetch
    try:
        data_agent.fetch_all_data()
        logging.info("Initial data fetch completed")
    except Exception as e:
        logging.error(f"Initial data fetch failed: {e}")

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())
