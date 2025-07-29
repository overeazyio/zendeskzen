import unittest
from zendesk_extractor.transformation import transform_to_structured_json, convert_to_xml
from zendesk_extractor.models import Ticket, Comment

class TestTransformation(unittest.TestCase):

    def test_transform_to_structured_json_success(self):
        ticket_data = {"id": 1, "created_at": "2023-01-01", "updated_at": "2023-01-01", "subject": "Test", "status": "open", "requester_id": 1, "assignee_id": 1, "tags": ["a", "b"]}
        comments_data = [{"id": 1, "author_id": 1, "body": "a comment", "created_at": "2023-01-01"}]
        ticket = transform_to_structured_json(ticket_data, comments_data)
        self.assertIsInstance(ticket, Ticket)
        self.assertEqual(ticket.ticket_id, 1)
        self.assertEqual(len(ticket.conversation), 1)
        self.assertEqual(ticket.conversation[0].comment_id, 1)

    def test_transform_to_structured_json_no_ticket_data(self):
        ticket = transform_to_structured_json(None, [])
        self.assertIsNone(ticket)

    def test_convert_to_xml_success(self):
        ticket = Ticket(
            ticket_id=1,
            created_at="2023-01-01",
            updated_at="2023-01-01",
            subject="Test",
            status="open",
            requester_id=1,
            assignee_id=1,
            tags=["a", "b"],
            conversation=[Comment(comment_id=1, author_id=1, body="a comment", created_at="2023-01-01")]
        )
        xml_string = convert_to_xml(ticket)
        self.assertIn("<ticket_id>1</ticket_id>", xml_string)
        self.assertIn("<subject>Test</subject>", xml_string)
        self.assertIn("<comment_id>1</comment_id>", xml_string)
        self.assertIn("<body>a comment</body>", xml_string)

    def test_convert_to_xml_no_ticket(self):
        xml_string = convert_to_xml(None)
        self.assertIsNone(xml_string)

if __name__ == '__main__':
    unittest.main()
