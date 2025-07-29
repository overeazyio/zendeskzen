from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Comment:
    """Represents a single comment in a Zendesk ticket.

    Attributes:
        comment_id: The unique identifier for the comment.
        author_id: The ID of the author of the comment.
        body: The content of the comment.
        created_at: The timestamp when the comment was created.
    """
    comment_id: int
    author_id: int
    body: str
    created_at: str

@dataclass
class Ticket:
    """Represents a Zendesk ticket, including its conversation history.

    Attributes:
        ticket_id: The unique identifier for the ticket.
        created_at: The timestamp when the ticket was created.
        updated_at: The timestamp when the ticket was last updated.
        subject: The subject of the ticket.
        status: The current status of the ticket.
        requester_id: The ID of the user who requested the ticket.
        assignee_id: The ID of the agent assigned to the ticket.
        tags: A list of tags associated with the ticket.
        conversation: A list of `Comment` objects representing the ticket's
                      conversation history.
    """
    ticket_id: int
    created_at: str
    updated_at: str
    subject: str
    status: str
    requester_id: int
    assignee_id: int
    tags: List[str]
    conversation: List[Comment] = field(default_factory=list)
