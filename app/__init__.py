# smart-healthcare-app/app/__init__.py
from flask import Flask, current_app
from flask_mysqldb import MySQL
from flask_cors import CORS
from flask_login import LoginManager
import os
try:
    import tensorflow as tf
except ImportError:
    tf = None
import logging
import datetime

mysql = MySQL()
login_manager = LoginManager()
login_manager.login_view = 'auth.login' # Redirect to login page if @login_required fails
login_manager.login_message_category = 'info' # For styling flashed messages

logger = logging.getLogger('app') # Main app logger

def load_tf_model(model_path_from_config):
    if tf is None:
        logger.warning("TensorFlow not installed. Diagnostics model will not be loaded.")
        return None
    if model_path_from_config and os.path.exists(model_path_from_config):
        try:
            # Suppress TensorFlow INFO/WARNING logs if they are too verbose during model loading
            # tf.get_logger().setLevel('ERROR') # Or 'FATAL'
            model = tf.keras.models.load_model(model_path_from_config, compile=False) # Added compile=False
            # If your model needs custom objects, pass them:
            # model = tf.keras.models.load_model(model_path_from_config, custom_objects={...}, compile=False)
            logger.info(f"TensorFlow diagnostics model loaded successfully from {model_path_from_config}")
            # Optionally compile if you need to evaluate metrics or continue training, 
            # but not strictly necessary for just predictions if it was saved with optimizer state.
            # model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy']) # Example
            return model
        except Exception as e:
            logger.error(f"Error loading TensorFlow diagnostics model from {model_path_from_config}: {e} (Type: {type(e)})", exc_info=True)
    else:
        logger.warning(f"Diagnostics model file not found at {model_path_from_config} or path not configured.")
    return None

def create_app(config_object):
    app = Flask(__name__)
    app.config.from_object(config_object)
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB Max Limit

    # Configure logging
    if app.config.get('DEBUG'):
        logging.basicConfig(level=logging.DEBUG)
        app.logger.setLevel(logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
        app.logger.setLevel(logging.INFO)
    
    global logger
    logger = app.logger

    mysql.init_app(app)
    CORS(app) 
    login_manager.init_app(app)

    if not hasattr(app, 'extensions'):
        app.extensions = {}
    
    model_path = app.config.get('TF_MODEL_PATH')
    app.extensions['diagnostics_model'] = load_tf_model(model_path)
    
    # Load Scaler
    import pickle
    scaler_path = os.path.join(os.path.dirname(model_path), 'scaler.pkl') if model_path else 'app/scaler.pkl'
    if os.path.exists(scaler_path):
        try:
            with open(scaler_path, 'rb') as f:
                app.extensions['diagnostics_scaler'] = pickle.load(f)
            logger.info(f"Diagnostics scaler loaded successfully from {scaler_path}")
        except Exception as e:
            logger.error(f"Error loading scaler from {scaler_path}: {e}")
            app.extensions['diagnostics_scaler'] = None
    else:
        logger.warning(f"Scaler file not found at {scaler_path}")
        app.extensions['diagnostics_scaler'] = None

    from .auth import auth as auth_blueprint
    from .mains import main as main_blueprint
    
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    app.register_blueprint(main_blueprint)

    from .models import User # Assuming models.py with User class
    @login_manager.user_loader
    def load_user(user_id):
        try:
            cur = mysql.connection.cursor()
            cur.execute("SELECT id, name, email FROM users WHERE id = %s", (user_id,))
            user_data = cur.fetchone()
            cur.close()
            if user_data:
                return User(id=user_data[0], name=user_data[1], email=user_data[2])
            logger.debug(f"User with id {user_id} not found in database.")
            return None
        except Exception as e:
            logger.error(f"Error loading user {user_id}: {e} (Type: {type(e)})", exc_info=True)
            return None

    @app.context_processor
    def inject_global_vars():
        return dict(current_year=datetime.datetime.now().year)

    return app