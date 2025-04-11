import os
from flask import Flask, render_template, current_app
from config import config_by_name
from api import blueprint as api_blueprint
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

    # Add a simple route for the root and the example form
    @app.route('/')
    def index():
        # Optionally, redirect to API docs or show a welcome message
        # For now, let's serve the subscribe form example
        return render_template('subscribe_form.html')

    @app.route('/subscribe-example')
    def subscribe_example():
        """Serves the example HTML form."""
        return render_template('subscribe_form.html')

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
