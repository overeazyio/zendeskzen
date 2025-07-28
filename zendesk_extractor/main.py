import os
import requests
from dotenv import load_dotenv

load_dotenv()

def get_zendesk_session():
    """
    Creates and returns a requests.Session object for interacting with the Zendesk API.
    """
    domain = os.getenv("ZENDESK_DOMAIN")
    email = os.getenv("ZENDESK_EMAIL")
    token = os.getenv("ZENDESK_API_TOKEN")

    if not all([domain, email, token]):
        raise ValueError("Zendesk API credentials not found in environment variables.")

    session = requests.Session()
    session.auth = (f"{email}/token", token)
    session.headers.update({"Accept": "application/json"})
    session.base_url = f"https://{domain}.zendesk.com/api/v2"
    return session
