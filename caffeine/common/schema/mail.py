from typing import Union, Sequence, List

from pydantic import BaseModel


class EmailAttachment(BaseModel):
    filename: str
    content_type: str
    data: bytes
    disposition: str = "attachment"
    headers: dict = {}


class EmailMessage(BaseModel):
    subject: str = None
    to: Union[str, Sequence[str]]
    body: str = None
    html: str = None
    from_address: str = None
    cc: Union[str, Sequence[str]] = None
    bcc: Union[str, Sequence[str]] = None
    attachments: List[EmailAttachment] = []
    reply_to: str = None
    date: int = None

    def add_attachment(self, *attachments: Union[EmailAttachment, Sequence[EmailAttachment]]):
        self.attachments.extend(attachments)
