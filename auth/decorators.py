import os
import time
import hmac
import hashlib
from functools import wraps
from flask import request, current_app, abort
import logging

log = logging.getLogger(__name__)

# Define the allowed time window in seconds (e.g., 5 minutes)
TIMESTAMP_WINDOW = 300

def signature_required(action_identifier):
    """
    Decorator to verify HMAC signature for API requests.
    Requires 'X-Timestamp' and 'X-Signature' headers.
    Signs the concatenation of timestamp + action_identifier.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 1. Get Secret Key
            api_secret = current_app.config.get('API_SECRET')
            if not api_secret:
                log.error("API_SECRET not configured on the server.")
                abort(500, "Authentication configuration error.") # Internal Server Error

            # 2. Get Headers
            timestamp_str = request.headers.get('X-Timestamp')
            received_signature = request.headers.get('X-Signature')

            if not timestamp_str or not received_signature:
                log.warning("Auth headers missing.")
                abort(401, "Missing required authentication headers (X-Timestamp, X-Signature).")

            # 3. Validate Timestamp
            try:
                request_timestamp = int(timestamp_str)
            except ValueError:
                log.warning(f"Invalid timestamp format received: {timestamp_str}")
                abort(401, "Invalid timestamp format.")

            current_timestamp = int(time.time())
            if abs(current_timestamp - request_timestamp) > TIMESTAMP_WINDOW:
                log.warning(f"Timestamp expired. Request: {request_timestamp}, Server: {current_timestamp}")
                abort(401, f"Timestamp expired or outside allowed window ({TIMESTAMP_WINDOW}s).")

            # 4. Construct Message & Calculate Expected Signature
            message = timestamp_str.encode('utf-8') + action_identifier.encode('utf-8')
            try:
                hash_obj = hmac.new(api_secret.encode('utf-8'), message, hashlib.sha256)
                expected_signature = hash_obj.hexdigest()
            except Exception as e:
                log.error(f"Error calculating HMAC: {e}")
                abort(500, "Error during signature verification.")

            # 5. Compare Signatures
            if not hmac.compare_digest(expected_signature, received_signature):
                log.warning(f"Signature mismatch. Received: {received_signature}, Expected: {expected_signature}")
                abort(401, "Invalid signature.")

            # 6. Proceed if valid
            log.debug(f"Signature verified successfully for action: {action_identifier}")
            return f(*args, **kwargs)
        return decorated_function
    return decorator
