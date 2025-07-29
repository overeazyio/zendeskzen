import os
import json
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


def save_as_json(ticket_id, data):
    """
    Saves the structured data as a JSON file.
    """
    directory = "output/json"
    os.makedirs(directory, exist_ok=True)
    filepath = os.path.join(directory, f"{ticket_id}.json")
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)


def save_as_xml(ticket_id, xml_string):
    """
    Saves the XML data as an XML file.
    """
    directory = "output/xml"
    os.makedirs(directory, exist_ok=True)
    filepath = os.path.join(directory, f"{ticket_id}.xml")
    with open(filepath, "w") as f:
        f.write(xml_string)


if __name__ == "__main__":
    # Example Usage (without making live API calls)
    # You can replace this with actual API calls if you have credentials

    # Sample raw data
    sample_ticket_data = {
        "id": 12345,
        "created_at": "2023-10-27T10:30:00Z",
        "updated_at": "2023-10-27T12:00:00Z",
        "subject": "Issue with billing",
        "status": "closed",
        "requester_id": 98765,
        "assignee_id": 54321,
        "tags": ["billing", "invoice"]
    }

    sample_comments_data = [
        {
            "id": 111,
            "author_id": 98765,
            "body": "Hello, I have a question about my recent invoice.",
            "created_at": "2023-10-27T10:30:00Z"
        },
        {
            "id": 222,
            "author_id": 54321,
            "body": "Hi there, I can help with that. What is your question?",
            "created_at": "2023-10-27T10:35:00Z"
        }
    ]

    # Import the transformation functions
    from transformation import transform_to_structured_json, convert_to_xml

    # 1. Transform to structured JSON
    structured_json = transform_to_structured_json(sample_ticket_data, sample_comments_data)
    print("Structured JSON:")
    import json
    print(json.dumps(structured_json, indent=2))

    # 2. Convert to XML
    xml_data = convert_to_xml(structured_json)
    print("\nXML Data:")
    print(xml_data)

    # 3. Save files
    ticket_id = sample_ticket_data["id"]
    save_as_json(ticket_id, structured_json)
    save_as_xml(ticket_id, xml_data)
    print(f"\nSaved ticket {ticket_id} as JSON and XML.")
