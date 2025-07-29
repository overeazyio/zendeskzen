from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Comment:
    comment_id: int
    author_id: int
    body: str
    created_at: str

@dataclass
class Ticket:
    ticket_id: int
    created_at: str
    updated_at: str
    subject: str
    status: str
    requester_id: int
    assignee_id: int
    tags: List[str]
    conversation: List[Comment] = field(default_factory=list)
