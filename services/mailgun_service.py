import requests
from flask import current_app

def _get_mailgun_auth():
    """Helper function to get Mailgun API authentication."""
    return ('api', current_app.config['MAILGUN_API_KEY'])

def _get_list_members_url():
    """Helper function to construct the list members URL."""
    list_address = current_app.config['MAILGUN_LIST_ADDRESS']
    base_url = current_app.config['MAILGUN_API_BASE_URL']
    return f"{base_url}/lists/{list_address}/members"

def _get_member_url(member_address):
    """Helper function to construct the specific member URL."""
    list_address = current_app.config['MAILGUN_LIST_ADDRESS']
    base_url = current_app.config['MAILGUN_API_BASE_URL']
    return f"{base_url}/lists/{list_address}/members/{member_address}"

def get_list_members():
    """Fetches all members from the configured Mailgun mailing list."""
    url = _get_list_members_url()
    auth = _get_mailgun_auth()
    try:
        response = requests.get(url, auth=auth)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json(), 200
    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"Mailgun API error (get_list_members): {e}")
        return {"message": f"Error fetching members: {e}"}, getattr(e.response, 'status_code', 500)

def add_list_member(email, name=None, subscribed=True, upsert=True):
    """Adds or updates a member in the configured Mailgun mailing list."""
    url = _get_list_members_url()
    auth = _get_mailgun_auth()
    data = {
        "address": email,
        "subscribed": str(subscribed).lower(),
        "upsert": str(upsert).lower()
    }
    if name:
        data["name"] = name

    print(data)
    # Mailgun expects form data, not JSON
    headers = {"Content-Type": "multipart/form-data"}

    try:
        response = requests.post(url, headers=headers, auth=auth, data=data)
        response.raise_for_status()
        return response.json(), response.status_code # Usually 200 OK or 201 Created if upsert=false
    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"Mailgun API error (add_list_member): {e}")
        error_message = f"Error adding member: {e}"
        status_code = getattr(e.response, 'status_code', 500)
        try:
            # Try to get more specific error from Mailgun response
            error_details = e.response.json()
            error_message = error_details.get('message', error_message)
        except (AttributeError, ValueError, TypeError):
            pass # Keep the original error message if parsing fails
        return {"message": error_message}, status_code


def get_member(member_address):
    """Fetches a specific member from the configured Mailgun mailing list."""
    url = _get_member_url(member_address)
    auth = _get_mailgun_auth()
    try:
        response = requests.get(url, auth=auth)
        response.raise_for_status()
        return response.json(), 200
    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"Mailgun API error (get_member): {e}")
        status_code = getattr(e.response, 'status_code', 500)
        if status_code == 404:
             return {"message": "Member not found"}, 404
        return {"message": f"Error fetching member: {e}"}, status_code


def update_member(member_address, name=None, subscribed=None):
    """Updates a specific member in the configured Mailgun mailing list."""
    url = _get_member_url(member_address)
    auth = _get_mailgun_auth()
    data = {}
    if name is not None:
        data["name"] = name
    if subscribed is not None:
        data["subscribed"] = str(subscribed).lower()

    if not data:
        return {"message": "No update data provided"}, 400

    # headers = {"Content-Type": "application/x-www-form-urlencoded"}

    try:
        response = requests.put(url, auth=auth, data=data)
        response.raise_for_status()
        return response.json(), 200
    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"Mailgun API error (update_member): {e}")
        status_code = getattr(e.response, 'status_code', 500)
        if status_code == 404:
             return {"message": "Member not found"}, 404
        return {"message": f"Error updating member: {e}"}, status_code


def delete_member(member_address):
    """Deletes a specific member from the configured Mailgun mailing list."""
    url = _get_member_url(member_address)
    auth = _get_mailgun_auth()
    try:
        response = requests.delete(url, auth=auth)
        response.raise_for_status()
        # Mailgun delete returns 200 OK on success
        return response.json(), 200
    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"Mailgun API error (delete_member): {e}")
        status_code = getattr(e.response, 'status_code', 500)
        if status_code == 404:
             return {"message": "Member not found"}, 404
        return {"message": f"Error deleting member: {e}"}, status_code
