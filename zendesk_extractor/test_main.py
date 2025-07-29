import unittest
from unittest.mock import patch, MagicMock
import requests
from zendesk_extractor.main import get_zendesk_session, fetch_tickets, fetch_ticket_comments, save_as_json, save_as_xml
from zendesk_extractor.exceptions import ZendeskAPIError, FileSaveError

class TestZendeskExtractor(unittest.TestCase):

    @patch('os.getenv')
    def test_get_zendesk_session_missing_credentials(self, mock_getenv):
        mock_getenv.return_value = None
        with self.assertRaises(ZendeskAPIError):
            get_zendesk_session()

    @patch('requests.Session')
    def test_fetch_tickets_request_exception(self, mock_session):
        mock_session.return_value.get.side_effect = requests.exceptions.RequestException("Test Exception")
        with self.assertRaises(ZendeskAPIError):
            fetch_tickets(mock_session.return_value)

    @patch('requests.Session')
    def test_fetch_ticket_comments_request_exception(self, mock_session):
        mock_session.return_value.get.side_effect = requests.exceptions.RequestException("Test Exception")
        with self.assertRaises(ZendeskAPIError):
            fetch_ticket_comments(mock_session.return_value, 123)

    @patch('requests.Session')
    def test_fetch_ticket_comments_not_found(self, mock_session):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_http_error = requests.exceptions.HTTPError()
        mock_http_error.response = mock_response
        mock_session.return_value.get.side_effect = mock_http_error
        with self.assertRaises(ZendeskAPIError):
            fetch_ticket_comments(mock_session.return_value, 123)

    @patch('builtins.open')
    def test_save_as_json_io_error(self, mock_open):
        mock_open.side_effect = IOError("Test IOError")
        with self.assertRaises(FileSaveError):
            save_as_json(123, MagicMock())

    @patch('builtins.open')
    def test_save_as_xml_io_error(self, mock_open):
        mock_open.side_effect = IOError("Test IOError")
        with self.assertRaises(FileSaveError):
            save_as_xml(123, "<xml></xml>")

if __name__ == '__main__':
    unittest.main()
