import os
from flask import Flask, render_template, current_app, redirect, url_for # Added redirect, url_for
import os
import time
import hmac
import hashlib
from flask import Flask, render_template, current_app
from config import config_by_name
from api import blueprint as api_blueprint # This now imports the blueprint from api/__init__.py
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def create_app(config_name=None):
    """Create and configure an instance of the Flask application."""
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'dev') # Default to 'dev' if not set

    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    # Register blueprints
    app.register_blueprint(api_blueprint)

    # Modify the root route to redirect to the example form
    @app.route('/')
    def index():
        # Redirect to the subscribe_example route which includes signature generation
        return redirect(url_for('subscribe_example')) # Changed this line

    @app.route('/subscribe-example')
    def subscribe_example():
        """Serves the example HTML form with pre-calculated signature data."""
        # Generate timestamp and signature for the example form
        # This mimics what Pelican would do during its build process
        api_secret = current_app.config.get('API_SECRET')
        # Ensure the action identifier matches the one used in the decorator for the POST endpoint
        # In api/mail_list.py, the POST endpoint uses 'subscribe-add'
        action_identifier = 'subscribe-add'
        timestamp = str(int(time.time()))
        signature = "ERROR_API_SECRET_NOT_SET" # Default in case secret is missing

        if api_secret:
            message = timestamp.encode('utf-8') + action_identifier.encode('utf-8')
            try:
                hash_obj = hmac.new(api_secret.encode('utf-8'), message, hashlib.sha256)
                signature = hash_obj.hexdigest()
                app.logger.debug(f"Generated signature for example form: {signature} (ts: {timestamp}, action: {action_identifier})")
            except Exception as e:
                app.logger.error(f"Error calculating HMAC for example form: {e}")
                signature = "ERROR_CALCULATING_SIGNATURE"
        else:
             app.logger.warning("API_SECRET not found, cannot generate signature for example form.")

        # Pass data to the template
        return render_template('subscribe_form.html',
                               api_timestamp=timestamp,
                               api_signature=signature,
                               api_action=action_identifier) # Pass action identifier too

    # Log the configuration being used
    app.logger.info(f"App created with configuration: {config_name}")
    app.logger.info(f"Mailgun List Address: {app.config.get('MAILGUN_LIST_ADDRESS')}")
    app.logger.info(f"Debug mode: {app.config.get('DEBUG')}")


    return app

# Create app instance for development server (e.g., flask run)
# For production, use a WSGI server like Gunicorn or uWSGI
if __name__ == '__main__':
    app = create_app()
    # Note: app.run() is suitable for development only.
    # Use a production WSGI server for deployment.
    app.run(debug=app.config['DEBUG']) # Use debug flag from config
