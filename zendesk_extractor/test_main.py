import unittest
from unittest.mock import patch, MagicMock, mock_open
import requests
import os
from zendesk_extractor.main import get_zendesk_session, fetch_tickets, fetch_ticket_comments, save_as_json, save_as_xml, main
from zendesk_extractor.exceptions import ZendeskAPIError, FileSaveError
from zendesk_extractor.models import Ticket, Comment

class TestZendeskExtractor(unittest.TestCase):

    @patch('os.getenv')
    def test_get_zendesk_session_success(self, mock_getenv):
        mock_getenv.side_effect = ['my_domain', 'my_email', 'my_token']
        session = get_zendesk_session()
        self.assertIsInstance(session, requests.Session)
        self.assertEqual(session.auth, ('my_email/token', 'my_token'))
        self.assertEqual(session.base_url, 'https://my_domain.zendesk.com/api/v2')

    @patch('os.getenv')
    def test_get_zendesk_session_missing_credentials(self, mock_getenv):
        mock_getenv.return_value = None
        with self.assertRaises(ZendeskAPIError):
            get_zendesk_session()

    @patch('requests.Session')
    def test_fetch_tickets_success(self, mock_session):
        mock_response = MagicMock()
        mock_response.json.return_value = {"results": [{"id": 1}], "meta": {"has_more": False}}
        mock_session.get.return_value = mock_response
        tickets = fetch_tickets(mock_session, start_time="2023-01-01")
        self.assertEqual(len(tickets), 1)
        self.assertEqual(tickets[0]['id'], 1)

    @patch('requests.Session')
    def test_fetch_tickets_request_exception(self, mock_session):
        mock_session.get.side_effect = requests.exceptions.RequestException("Test Exception")
        with self.assertRaises(ZendeskAPIError):
            fetch_tickets(mock_session)

    @patch('requests.Session')
    def test_fetch_ticket_comments_success(self, mock_session):
        mock_response = MagicMock()
        mock_response.json.return_value = {"comments": [{"id": 1, "body": "a comment"}]}
        mock_session.get.return_value = mock_response
        comments = fetch_ticket_comments(mock_session, 123)
        self.assertEqual(len(comments), 1)
        self.assertEqual(comments[0]['id'], 1)

    @patch('requests.Session')
    def test_fetch_ticket_comments_request_exception(self, mock_session):
        mock_session.get.side_effect = requests.exceptions.RequestException("Test Exception")
        with self.assertRaises(ZendeskAPIError):
            fetch_ticket_comments(mock_session, 123)

    @patch('requests.Session')
    def test_fetch_ticket_comments_not_found(self, mock_session):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_http_error = requests.exceptions.HTTPError()
        mock_http_error.response = mock_response
        mock_session.get.side_effect = mock_http_error
        with self.assertRaises(ZendeskAPIError):
            fetch_ticket_comments(mock_session, 123)

    @patch('builtins.open', new_callable=mock_open)
    @patch('os.makedirs')
    def test_save_as_json_success(self, mock_makedirs, mock_file):
        ticket = Ticket(ticket_id=1, created_at="2023-01-01", updated_at="2023-01-01", subject="Test", status="open", requester_id=1, assignee_id=1, tags=[])
        save_as_json(1, ticket)
        mock_makedirs.assert_called_once_with("output/json", exist_ok=True)
        mock_file.assert_called_once_with(os.path.join("output/json", "1.json"), "w")

    @patch('builtins.open', new_callable=mock_open)
    def test_save_as_json_io_error(self, mock_open):
        mock_open.side_effect = IOError("Test IOError")
        with self.assertRaises(FileSaveError):
            save_as_json(123, MagicMock())

    @patch('builtins.open', new_callable=mock_open)
    @patch('os.makedirs')
    def test_save_as_xml_success(self, mock_makedirs, mock_file):
        save_as_xml(1, "<xml></xml>")
        mock_makedirs.assert_called_once_with("output/xml", exist_ok=True)
        mock_file.assert_called_once_with(os.path.join("output/xml", "1.xml"), "w")


    @patch('builtins.open', new_callable=mock_open)
    def test_save_as_xml_io_error(self, mock_open):
        mock_open.side_effect = IOError("Test IOError")
        with self.assertRaises(FileSaveError):
            save_as_xml(123, "<xml></xml>")

    @patch('zendesk_extractor.main.get_zendesk_session')
    @patch('zendesk_extractor.main.fetch_tickets')
    @patch('zendesk_extractor.main.fetch_ticket_comments')
    @patch('zendesk_extractor.main.transform_to_structured_json')
    @patch('zendesk_extractor.main.convert_to_xml')
    @patch('zendesk_extractor.main.save_as_json')
    @patch('zendesk_extractor.main.save_as_xml')
    def test_main_success(self, mock_save_xml, mock_save_json, mock_convert_xml, mock_transform_json, mock_fetch_comments, mock_fetch_tickets, mock_get_session):
        mock_get_session.return_value = MagicMock()
        mock_fetch_tickets.return_value = [{"id": 1}]
        mock_fetch_comments.return_value = [{"id": 1, "body": "a comment"}]
        mock_transform_json.return_value = MagicMock()
        mock_convert_xml.return_value = "<xml></xml>"
        main()
        mock_save_json.assert_called_once()
        mock_save_xml.assert_called_once()


if __name__ == '__main__':
    unittest.main()
