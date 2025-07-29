import os
import json
import requests
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional
from requests import Session
from zendesk_extractor.core.transformation import transform_to_structured_json, convert_to_xml
from zendesk_extractor.core.models import Ticket
from dataclasses import asdict
from zendesk_extractor.core.exceptions import ZendeskAPIError

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_zendesk_session() -> Session:
    """Creates and returns a requests.Session object for interacting with the Zendesk API.

    This function retrieves Zendesk API credentials (domain, email, and token) from
    environment variables, validates their presence, and initializes a requests.Session
    object with the necessary authentication headers and base URL.

    Returns:
        A requests.Session object configured for the Zendesk API.

    Raises:
        ZendeskAPIError: If the API credentials are not found in the environment
                         variables or if the session creation fails.
    """
    try:
        domain = os.getenv("ZENDESK_DOMAIN")
        email = os.getenv("ZENDESK_EMAIL")
        token = os.getenv("ZENDESK_API_TOKEN")

        if not all([domain, email, token]):
            raise ZendeskAPIError("Zendesk API credentials not found in environment variables.")

        session = requests.Session()
        session.auth = (f"{email}/token", token)
        session.headers.update({"Accept": "application/json"})
        session.base_url = f"https://{domain}.zendesk.com/api/v2"
        return session
    except Exception as e:
        raise ZendeskAPIError(f"Failed to create Zendesk session: {e}")

def fetch_tickets(session: Session, start_time: Optional[str] = None) -> Optional[List[Dict[str, Any]]]:
    """Retrieves a list of tickets from Zendesk, handling API pagination.

    This function queries the Zendesk search API for tickets created after a specified
    time. It automatically handles pagination to fetch all available tickets.

    Args:
        session: The requests.Session object for making API calls.
        start_time: An optional ISO 8601 formatted date string to filter tickets
                    created after this time.

    Returns:
        A list of ticket dictionaries, or None if no tickets are found.

    Raises:
        ZendeskAPIError: If an error occurs while fetching tickets from the API.
    """
    tickets = []
    url = f"{session.base_url}/search.json"
    params = {}

    if start_time:
        params["query"] = f"type:ticket updated>={start_time}"

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
            raise ZendeskAPIError(f"An error occurred while fetching tickets: {e}")

    return tickets

def fetch_ticket_comments(session: Session, ticket_id: int) -> Optional[List[Dict[str, Any]]]:
    """Retrieves all comments for a single ticket, handling pagination.

    This function fetches all comments for a given ticket ID, automatically
    handling pagination to ensure all comments are retrieved.

    Args:
        session: The requests.Session object for making API calls.
        ticket_id: The ID of the ticket to fetch comments for.

    Returns:
        A list of comment dictionaries, or None if no comments are found.

    Raises:
        ZendeskAPIError: If the ticket is not found or an error occurs while
                         fetching comments.
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
                raise ZendeskAPIError(f"Ticket with ID {ticket_id} not found.")
            else:
                raise ZendeskAPIError(f"An HTTP error occurred while fetching comments for ticket {ticket_id}: {e}")
        except requests.exceptions.RequestException as e:
            raise ZendeskAPIError(f"An error occurred while fetching comments for ticket {ticket_id}: {e}")

    return comments


from zendesk_extractor.core.exceptions import FileSaveError

def save_data_to_file(ticket_id: int, data: Any, file_extension: str) -> None:
    """Saves data to a file with the given extension.

    This function saves the given data to a file in the corresponding
    `output/{file_extension}` directory. The filename is based on the ticket ID.

    Args:
        ticket_id: The ID of the ticket, used for the filename.
        data: The data to be saved.
        file_extension: The extension of the file (e.g., "json" or "xml").

    Raises:
        FileSaveError: If an error occurs while saving the file.
    """
    try:
        directory = f"output/{file_extension}"
        os.makedirs(directory, exist_ok=True)
        filepath = os.path.join(directory, f"{ticket_id}.{file_extension}")
        with open(filepath, "w") as f:
            if file_extension == "json":
                json.dump(asdict(data), f, indent=2)
            else:
                f.write(data)
    except (IOError, OSError) as e:
        raise FileSaveError(f"Error saving {file_extension.upper()} file for ticket {ticket_id}: {e}")


def save_as_json(ticket_id: int, data: Ticket) -> None:
    """Saves the structured data as a JSON file.

    This function saves the given Ticket object as a JSON file by calling
    the generic save_data_to_file function.

    Args:
        ticket_id: The ID of the ticket, used for the filename.
        data: The Ticket object to be saved.
    """
    save_data_to_file(ticket_id, data, "json")


def save_as_xml(ticket_id: int, xml_string: str) -> None:
    """Saves the XML data as an XML file.

    This function saves the given XML string as an XML file by calling
    the generic save_data_to_file function.

    Args:
        ticket_id: The ID of the ticket, used for the filename.
        xml_string: The XML content to be saved.
    """
    save_data_to_file(ticket_id, xml_string, "xml")


from zendesk_extractor.core.exceptions import ZendeskExtractorError

def main() -> None:
    """Main function to orchestrate the Zendesk ticket processing.

    This function orchestrates the entire process of fetching tickets from Zendesk,
    transforming them into structured JSON and XML formats, and saving them to files.
    It handles errors gracefully and logs the progress.
    """
    try:
        session = get_zendesk_session()

        last_run_file = "last_run.txt"
        try:
            with open(last_run_file, "r") as f:
                start_date = f.read().strip()
        except FileNotFoundError:
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

            except ZendeskExtractorError as e:
                logging.error(f"An error occurred while processing ticket {ticket_id}: {e}")
                continue

        with open(last_run_file, "w") as f:
            f.write(datetime.now().isoformat())

    except ZendeskExtractorError as e:
        logging.error(f"An unrecoverable error occurred: {e}")

if __name__ == "__main__":
    main()
