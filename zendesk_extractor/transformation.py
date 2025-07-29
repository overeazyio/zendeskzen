import xml.etree.ElementTree as ET
from typing import Dict, Any, List, Optional
from models import Ticket, Comment
from dataclasses import asdict

def transform_to_structured_json(ticket_data: Dict[str, Any], comments_data: List[Dict[str, Any]]) -> Optional[Ticket]:
    """
    Transforms raw ticket and comment data into a structured JSON format.
    """
    if not ticket_data:
        return None

    conversation = []
    if comments_data:
        for comment in comments_data:
            conversation.append(Comment(
                comment_id=comment.get("id"),
                author_id=comment.get("author_id"),
                body=comment.get("body"),
                created_at=comment.get("created_at")
            ))

    return Ticket(
        ticket_id=ticket_data.get("id"),
        created_at=ticket_data.get("created_at"),
        updated_at=ticket_data.get("updated_at"),
        subject=ticket_data.get("subject"),
        status=ticket_data.get("status"),
        requester_id=ticket_data.get("requester_id"),
        assignee_id=ticket_data.get("assignee_id"),
        tags=ticket_data.get("tags"),
        conversation=conversation
    )


def convert_to_xml(ticket: Ticket) -> Optional[str]:
    """
    Converts a Ticket object to an XML string.
    """
    if not ticket:
        return None

    structured_data = asdict(ticket)
    root = ET.Element("ticket")

    for key, value in structured_data.items():
        if key == "conversation":
            conversation_element = ET.SubElement(root, "conversation")
            for comment_data in value:
                comment_element = ET.SubElement(conversation_element, "comment")
                for k, v in comment_data.items():
                    sub_element = ET.SubElement(comment_element, k)
                    sub_element.text = str(v)
        elif key == "tags" and isinstance(value, list):
            tags_element = ET.SubElement(root, "tags")
            for tag in value:
                tag_element = ET.SubElement(tags_element, "tag")
                tag_element.text = tag
        else:
            element = ET.SubElement(root, key)
            element.text = str(value)

    return ET.tostring(root, encoding="unicode")
