import os
import json
import requests
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional
from requests import Session
from transformation import transform_to_structured_json, convert_to_xml
from models import Ticket
from dataclasses import asdict

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_zendesk_session() -> Session:
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

def fetch_tickets(session: Session, start_time: Optional[str] = None) -> Optional[List[Dict[str, Any]]]:
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

def fetch_ticket_comments(session: Session, ticket_id: int) -> Optional[List[Dict[str, Any]]]:
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


def save_as_json(ticket_id: int, data: Ticket) -> None:
    """
    Saves the structured data as a JSON file.
    """
    directory = "output/json"
    os.makedirs(directory, exist_ok=True)
    filepath = os.path.join(directory, f"{ticket_id}.json")
    with open(filepath, "w") as f:
        json.dump(asdict(data), f, indent=2)


def save_as_xml(ticket_id: int, xml_string: str) -> None:
    """
    Saves the XML data as an XML file.
    """
    directory = "output/xml"
    os.makedirs(directory, exist_ok=True)
    filepath = os.path.join(directory, f"{ticket_id}.xml")
    with open(filepath, "w") as f:
        f.write(xml_string)


def main() -> None:
    """
    Main function to orchestrate the Zendesk ticket processing.
    """
    try:
        session = get_zendesk_session()
    except ValueError as e:
        logging.error(f"Failed to initialize Zendesk session: {e}")
        return

    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    tickets = fetch_tickets(session, start_time=start_date)

    if not tickets:
        logging.info("No tickets found for the specified period.")
        return

    logging.info(f"Found {len(tickets)} tickets.")

    for ticket in tickets:
        ticket_id = ticket["id"]
        logging.info(f"Processing ticket ID: {ticket_id}")
        try:
            comments = fetch_ticket_comments(session, ticket_id)
            if comments is None:
                logging.warning(f"Could not fetch comments for ticket {ticket_id}. Skipping.")
                continue

            structured_data = transform_to_structured_json(ticket, comments)
            if structured_data is None:
                logging.warning(f"Could not transform data for ticket {ticket_id}. Skipping.")
                continue

            save_as_json(ticket_id, structured_data)

            xml_data = convert_to_xml(structured_data)
            if xml_data is None:
                logging.warning(f"Could not convert data to XML for ticket {ticket_id}. Skipping.")
                continue

            save_as_xml(ticket_id, xml_data)

            logging.info(f"Successfully processed and saved ticket ID: {ticket_id}")

        except Exception as e:
            logging.error(f"An unexpected error occurred while processing ticket {ticket_id}: {e}")
            continue

if __name__ == "__main__":
    main()
