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
    # doc='/docs' # Optional: path for Swagger UI documentation
)

# Add namespaces to the API
api.add_namespace(mail_list_ns, path='/mail-list') # Route will be /api/v1/mail-list
