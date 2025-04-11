# Ephergent API

API for managing Mailgun mailing list subscribers for the Ephergent blog.

## Features

*   Provides a RESTful API (`/api/v1/mail-list/subscribers`) for CRUD operations on mailing list members.
*   Uses Mailgun API for backend operations.
*   Built with Flask and Flask-RESTX.
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
        *   Set `FLASK_CONFIG` to `dev` for development or `prod` for production.
        *   Set `FLASK_DEBUG` to `1` for development (enables debug mode and auto-reloader).

5.  **Run the development server:**
    ```bash
    flask run
    ```
    The API will be available at `http://127.0.0.1:5000` (or the port specified by Flask).
    *   API base URL: `http://127.0.0.1:5000/api/v1/mail-list`
    *   API endpoints: `/subscribers`, `/subscribers/<email>`
    *   Example form: `http://127.0.0.1:5000/subscribe-example`
    *   Swagger UI Docs (if enabled in `api/__init__.py`): `http://127.0.0.1:5000/api/v1/mail-list/docs` (or path specified)

## API Endpoints

Base URL: `/api/v1/mail-list`

*   **`GET /subscribers`**: List all subscribers.
*   **`POST /subscribers`**: Add a new subscriber or update an existing one (if `upsert=true`, default).
    *   Requires `address` (email) in form data or JSON body.
    *   Optional: `name`, `subscribed` (boolean), `upsert` (boolean).
*   **`GET /subscribers/<member_address>`**: Get details for a specific subscriber by email address.
*   **`PUT /subscribers/<member_address>`**: Update a specific subscriber.
    *   Optional: `name`, `subscribed` (boolean) in form data or JSON body.
*   **`DELETE /subscribers/<member_address>`**: Delete a specific subscriber.

## Deployment

For production, use a proper WSGI server like Gunicorn or uWSGI. Example with Gunicorn:

```bash
pip install gunicorn
gunicorn --bind 0.0.0.0:8000 "app:create_app('prod')"
```
Ensure `FLASK_CONFIG` is set to `prod` and `FLASK_DEBUG` is `0` in your production environment.

