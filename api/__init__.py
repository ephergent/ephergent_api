from flask import Blueprint
from flask_restx import Api

# Import namespaces
from .mail_list import api as mail_list_ns

# Create Blueprint
# It's common to prefix API routes, e.g., '/api/v1'
blueprint = Blueprint('api', __name__, url_prefix='/api/v1')

# Initialize API with Flask-RESTX
api = Api(
    blueprint,
    title='Ephergent API',
    version='1.0',
    description='API for managing Mailgun mailing list subscribers',
    doc='/docs' # Optional: path for Swagger UI documentation
)

# Add namespaces to the API
api.add_namespace(mail_list_ns, path='/mail-list') # Route will be /api/v1/mail-list
from flask import Blueprint
from flask_restx import Api
import logging

# Import namespaces
from .mail_list import api as mail_list_ns
# Add other namespaces here if any

log = logging.getLogger(__name__)

blueprint = Blueprint('api', __name__, url_prefix='/api/v1')

# Define security scheme for Swagger UI
authorizations = {
    'apiKey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'X-Signature', # Primary header for Swagger UI auth button
        'description': "HMAC Signature (X-Signature) and Timestamp (X-Timestamp) required. Enter the signature here if testing via Swagger, but ensure X-Timestamp is also provided via other means (e.g., browser dev tools)."
    }
}

# Initialize API with blueprint, title, description, and security definitions
# Note: The path in mail_list.py (@api.route('/')) is relative to the namespace path here.
api = Api(
    blueprint,
    title='Ephergent API - Subscribers',
    version='1.0',
    description='API for Ephergent mailing list subscriber management.',
    doc='/doc/', # Path for Swagger UI relative to blueprint prefix (/api/v1/doc/)
    authorizations=authorizations,
    # security='apiKey' # Optional: Apply globally if ALL endpoints need auth
)

# Add namespaces to the API
# The final endpoint will be blueprint_prefix + namespace_path + route_path
# e.g., /api/v1 + /mail + / = /api/v1/mail/
api.add_namespace(mail_list_ns, path='/mail')
# Add other namespaces

log.info("API Blueprint created with namespaces and security definitions.")
