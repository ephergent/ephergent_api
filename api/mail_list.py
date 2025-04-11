from flask import request
from flask_restx import Namespace, Resource, fields, reqparse
from services import mailgun_service
import logging
from auth.decorators import signature_required # Import the decorator

# Setup logging
log = logging.getLogger(__name__)

# Define the namespace
api = Namespace('subscribers', description='Mailgun mailing list subscriber operations')

# Define data models for request/response serialization and documentation
subscriber_model = api.model('Subscriber', {
    'address': fields.String(required=True, description='Email address of the subscriber'),
    'name': fields.String(description='Name of the subscriber'),
    'subscribed': fields.Boolean(description='Subscription status'),
    # Add other relevant fields returned by Mailgun if needed
    # 'vars': fields.Raw(description='Custom variables')
})

message_model = api.model('Message', {
    'message': fields.String(required=True, description='A message describing the result')
})

# Parser for adding a subscriber (POST) - handles form data, JSON, and query parameters
subscriber_parser = reqparse.RequestParser()
subscriber_parser.add_argument('address', type=str, required=True, help='Email address cannot be blank', location=('json', 'form', 'args'))
subscriber_parser.add_argument('name', type=str, help='Optional subscriber name', required=False, location=('json', 'form', 'args'))
subscriber_parser.add_argument('subscribed', type=bool, help='Subscription status (default: true)', default=True, location=('json', 'form', 'args'))
subscriber_parser.add_argument('upsert', type=bool, help='Update if exists (default: true)', default=True, location=('json', 'form', 'args'))


# Parser for updating a subscriber (PUT) - handles form data, JSON, and query parameters
update_subscriber_parser = reqparse.RequestParser()
update_subscriber_parser.add_argument('name', type=str, help='Optional subscriber name', required=False, location=('json', 'form', 'args'))
update_subscriber_parser.add_argument('subscribed', type=bool, help='Subscription status', required=False, location=('json', 'form', 'args'))


@api.route('/')
class SubscriberList(Resource):
    """Shows a list of all subscribers, and lets you POST to add new subscribers."""

    @api.doc('list_subscribers')
    # @api.marshal_list_with(subscriber_model) # Mailgun returns a complex structure, maybe just return raw JSON
    @api.response(200, 'Success')
    @api.response(500, 'Mailgun API Error')
    def get(self):
        """List all subscribers"""
        log.info("Received request to list subscribers")
        result, status_code = mailgun_service.get_list_members()
        return result, status_code

    @api.doc('create_subscriber', security='apiKey', params={
            'X-Timestamp': {'in': 'header', 'description': 'Request timestamp (Unix epoch seconds)', 'required': True},
            'X-Signature': {'in': 'header', 'description': 'HMAC-SHA256 signature of (timestamp + "subscribe-add")', 'required': True}
    })
    @api.expect(subscriber_parser)
    @api.response(200, 'Subscriber added or updated successfully', message_model)
    @api.response(400, 'Input validation error')
    @api.response(401, 'Authentication Error (timestamp/signature invalid)')
    @api.response(500, 'Mailgun API Error')
    @signature_required('subscribe-add') # Apply decorator with action identifier
    def post(self):
        """Create a new subscriber (or update if upsert=true)"""
        args = subscriber_parser.parse_args()
        log.info(f"Received request to add/update subscriber: {args['address']}")
        result, status_code = mailgun_service.add_list_member(
            email=args['address'],
            name=args.get('name'), # Use get for optional args
            subscribed=args['subscribed'],
            upsert=args['upsert']
        )
        return result, status_code


@api.route('/<string:member_address>')
@api.param('member_address', 'The email address of the subscriber')
@api.response(404, 'Subscriber not found', message_model)
@api.response(500, 'Mailgun API Error')
class Subscriber(Resource):
    """Show a single subscriber item and lets you update or delete them"""

    @api.doc('get_subscriber')
    # @api.marshal_with(subscriber_model) # Mailgun returns a complex structure
    @api.response(200, 'Success')
    def get(self, member_address):
        """Fetch a specific subscriber"""
        log.info(f"Received request to get subscriber: {member_address}")
        result, status_code = mailgun_service.get_member(member_address)
        return result, status_code

    @api.doc('update_subscriber', security='apiKey', params={
            'X-Timestamp': {'in': 'header', 'description': 'Request timestamp (Unix epoch seconds)', 'required': True},
            'X-Signature': {'in': 'header', 'description': 'HMAC-SHA256 signature of (timestamp + "subscribe-update")', 'required': True}
    })
    @api.expect(update_subscriber_parser)
    @api.response(200, 'Subscriber updated successfully', message_model)
    @api.response(400, 'Input validation error or no data provided')
    @api.response(401, 'Authentication Error (timestamp/signature invalid)')
    @signature_required('subscribe-update') # Apply decorator with action identifier
    def put(self, member_address):
        """Update a subscriber"""
        args = update_subscriber_parser.parse_args()
        log.info(f"Received request to update subscriber: {member_address}")
        # Filter out None values so we only send provided fields
        update_data = {k: v for k, v in args.items() if v is not None}

        if not update_data:
             api.abort(400, "No update data provided. Provide 'name' or 'subscribed'.")

        result, status_code = mailgun_service.update_member(
            member_address=member_address,
            **update_data # Pass filtered args
        )
        return result, status_code

    @api.doc('delete_subscriber', security='apiKey', params={
            'X-Timestamp': {'in': 'header', 'description': 'Request timestamp (Unix epoch seconds)', 'required': True},
            'X-Signature': {'in': 'header', 'description': 'HMAC-SHA256 signature of (timestamp + "subscribe-delete")', 'required': True}
    })
    @api.response(200, 'Subscriber deleted successfully', message_model) # Mailgun returns 200 on delete
    @api.response(401, 'Authentication Error (timestamp/signature invalid)')
    @signature_required('subscribe-delete') # Apply decorator with action identifier
    def delete(self, member_address):
        """Delete a subscriber"""
        log.info(f"Received request to delete subscriber: {member_address}")
        result, status_code = mailgun_service.delete_member(member_address)
        return result, status_code
