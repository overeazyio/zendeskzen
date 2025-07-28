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

def fetch_tickets(session, start_time=None):
    """
    Retrieves a list of tickets from Zendesk, handling API pagination.
    """
    tickets = []
    url = f"{session.base_url}/search.json"
    params = {}

    if start_time:
        params["query"] = f"type:ticket created>={start_time}"

    while url:
        try:
            response = session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            tickets.extend(data["results"])

            if data.get("meta", {}).get("has_more"):
                url = data["links"]["next"]
                params = {}  # Clear params for subsequent requests as the full URL is provided
            else:
                url = None

        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            return None

    return tickets

def fetch_ticket_comments(session, ticket_id):
    """
    Retrieves all comments for a single ticket, handling pagination.
    """
    comments = []
    url = f"{session.base_url}/tickets/{ticket_id}/comments.json"

    while url:
        try:
            response = session.get(url)
            response.raise_for_status()
            data = response.json()
            comments.extend(data["comments"])
            url = data.get("next_page")

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                print(f"Ticket with ID {ticket_id} not found.")
                return None
            else:
                print(f"An HTTP error occurred: {e}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            return None

    return comments
