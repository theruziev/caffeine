from pydantic import BaseModel


class PubSubMessage(BaseModel):
    uuid: str
    channel: str
    data: dict = None
    is_done: bool = False
    created_at: int
    updated_at: int
