# smart-healthcare-app/run.py
from app import create_app
from config import current_config
import os

os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0' # If needed for your TensorFlow setup

app = create_app(current_config)

if __name__ == "__main__":
    app.run(debug=app.config.get('DEBUG', False), host='0.0.0.0', port=5000)