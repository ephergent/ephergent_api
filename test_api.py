import time
import hashlib
import hmac
import requests
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:5000/api/v1/mail/subscribers")
API_SECRET = os.getenv("API_SECRET", "YOUR_API_SECRET").encode()  # Convert to bytes

def generate_signature(action):
    timestamp = str(int(time.time()))
    message = f"{timestamp}{action}"
    signature = hmac.new(API_SECRET, message.encode(), hashlib.sha256).hexdigest()
    return timestamp, signature

def test_list_subscribers():
    response = requests.get(BASE_URL + "/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data.get("items"), list)

def test_add_subscriber():
    timestamp, signature = generate_signature("subscribe-add")
    headers = {
        "X-Timestamp": timestamp,
        "X-Signature": signature,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"address": "test@example.com"}
    response = requests.post(BASE_URL + "/", headers=headers, data=data)
    assert response.status_code in [200, 201]

def test_get_subscriber():
    response = requests.get(BASE_URL + "/test@example.com")
    assert response.status_code == 200
    data = response.json()
    assert "member" in data
    assert "address" in data["member"]

def test_update_subscriber():
    timestamp, signature = generate_signature("subscribe-update")
    headers = {
        "X-Timestamp": timestamp,
        "X-Signature": signature,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"name": "Test User"}
    response = requests.put(BASE_URL + "/test@example.com", headers=headers, data=data)
    assert response.status_code == 200

def test_delete_subscriber():
    timestamp, signature = generate_signature("subscribe-delete")
    headers = {
        "X-Timestamp": timestamp,
        "X-Signature": signature
    }
    response = requests.delete(BASE_URL + "/test@example.com", headers=headers)
    assert response.status_code in [200, 204]
