import os
import sys

# Add the project root to the path so 'app' can be found
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from config import current_config

app = create_app(current_config)

# Vercel needs 'app' to be exported
# Flask-MySQLdb might need explicit configuration or a hosted MySQL instance
# For Vercel, we often use environment variables for DB connection
