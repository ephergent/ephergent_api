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
# Ensure this matches the path used in the HTML form
api.add_namespace(mail_list_ns, path='/mail/subscribers')

log.info("API Blueprint created with namespaces and security definitions.")
