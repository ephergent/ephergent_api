# Ephergent API

API for managing Mailgun mailing list subscribers for the Ephergent blog.

## Features

*   Provides a RESTful API (`/api/v1/mail/subscribers`) for CRUD operations on mailing list members.
*   Uses Mailgun API for backend operations.
*   HMAC-based authentication for secure API access.
*   Built with Flask and Flask-RESTX with Swagger UI documentation.
*   Includes an example HTML form for subscribing.

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd ephergent_api
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    # On Windows use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure environment variables:**
    *   Copy the example environment file:
        ```bash
        cp env-example .env
        ```
    *   Edit the `.env` file and fill in your details:
        *   `SECRET_KEY`: Generate a strong secret key (e.g., using `openssl rand -hex 32`).
        *   `MAILGUN_API_KEY`: Your Mailgun API key (the one starting with `key-...`).
        *   `MAILGUN_LIST_ADDRESS`: The full address of your Mailgun mailing list (e.g., `mylist@mg.yourdomain.com`).
        *   `API_SECRET`: Secret key used for API request signing.
        *   Set `FLASK_CONFIG` to `dev` for development or `prod` for production.
        *   Set `FLASK_DEBUG` to `1` for development (enables debug mode and auto-reloader).

5.  **Run the development server:**
    ```bash
    flask run
    ```
    The API will be available at `http://127.0.0.1:5000` (or the port specified by Flask).
    *   API base URL: `http://127.0.0.1:5000/api/v1/mail/subscribers`
    *   API endpoints: `/` (list/create), `/<email>` (get/update/delete)
    *   Example form: `http://127.0.0.1:5000/subscribe-example`
    *   Swagger UI Docs: `http://127.0.0.1:5000/api/v1/doc/`

## API Endpoints

Base URL: `/api/v1/mail/subscribers`

*   **`GET /`**: List all subscribers.
*   **`POST /`**: Add a new subscriber or update an existing one (if `upsert=true`, default).
    *   Requires `address` (email) in form data or JSON body.
    *   Optional: `name`, `subscribed` (boolean), `upsert` (boolean).
    *   Requires authentication headers (`X-Timestamp`, `X-Signature`).
*   **`GET /<member_address>`**: Get details for a specific subscriber by email address.
*   **`PUT /<member_address>`**: Update a specific subscriber.
    *   Optional: `name`, `subscribed` (boolean) in form data or JSON body.
    *   Requires authentication headers (`X-Timestamp`, `X-Signature`).
*   **`DELETE /<member_address>`**: Delete a specific subscriber.
    *   Requires authentication headers (`X-Timestamp`, `X-Signature`).

## Authentication

Protected endpoints (POST, PUT, DELETE) require HMAC-based authentication using two HTTP headers:

*   **`X-Timestamp`**: Current Unix timestamp in seconds
*   **`X-Signature`**: HMAC-SHA256 signature of the timestamp and action identifier

The signature is calculated as:
```
HMAC-SHA256(timestamp + action_identifier, API_SECRET)
```

Where:
- `timestamp` is the Unix epoch timestamp in seconds
- `action_identifier` is a specific string for each operation:
  - POST (add): `subscribe-add`
  - PUT (update): `subscribe-update`
  - DELETE (delete): `subscribe-delete`
- `API_SECRET` is the server's secret key from your environment variables

### Example in Python

```python
import time
import hmac
import hashlib

# Your API secret
api_secret = "your_api_secret_key"

# Current timestamp
timestamp = str(int(time.time()))

# Action identifier (depends on the operation)
action = "subscribe-add"  # For POST requests

# Calculate signature
message = timestamp.encode('utf-8') + action.encode('utf-8')
signature = hmac.new(api_secret.encode('utf-8'), message, hashlib.sha256).hexdigest()

# Use these values in your HTTP headers
# X-Timestamp: timestamp
# X-Signature: signature
```

### Example Curl Command

```bash
# Generate current timestamp
TIMESTAMP=$(date +%s)

# Define action identifier
ACTION="subscribe-add"

# Calculate signature
API_SECRET="your_api_secret_key"
SIGNATURE=$(echo -n "${TIMESTAMP}${ACTION}" | openssl dgst -sha256 -hmac "${API_SECRET}" | cut -d ' ' -f2)

# Make the API call
curl -X POST "http://127.0.0.1:5000/api/v1/mail/subscribers/" \
    -H "X-Timestamp: ${TIMESTAMP}" \
    -H "X-Signature: ${SIGNATURE}" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "address=user@example.com&name=Test%20User"
```

## Using the Swagger UI

1. Navigate to `/api/v1/doc/` to access the Swagger UI
2. Click on an endpoint to expand it
3. For protected endpoints:
   - Click the lock icon (Authorize)
   - Enter the `X-Signature` value
   - In the Parameters section, add the `X-Timestamp` header manually
4. Fill in the required parameters
5. Click "Execute" to test the endpoint

## Example Subscription Form

An example HTML form for subscribing to the mailing list is available at `/subscribe-example`. This form:

- Demonstrates client-side signature calculation
- Shows how to handle the API response
- Can be used as a template for integration with your website

## Security Notes

- Signatures are valid for 5 minutes by default (configurable via `TIMESTAMP_WINDOW` in `decorators.py`)
- Always use HTTPS in production
- Keep your `API_SECRET` secure and don't expose it in client-side code

## Deployment

For production, use a proper WSGI server like Gunicorn or uWSGI. Example with Gunicorn:

```bash
pip install gunicorn
gunicorn --bind 0.0.0.0:8000 "app:create_app('prod')"
```

Ensure `FLASK_CONFIG` is set to `prod` and `FLASK_DEBUG` is `0` in your production environment.

For a more robust deployment, consider using:
- A reverse proxy (Nginx/Apache) in front of your app
- SSL/TLS certificates for HTTPS
- Process management tools (Supervisor/systemd)