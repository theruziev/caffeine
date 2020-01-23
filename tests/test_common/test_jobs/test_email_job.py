import secrets
from uuid import uuid4

import httpx
import pendulum
import pytest
from async_sender import Mail
from asynctest import Mock

from caffeine.common.job.email import EmailJob
from caffeine.common.schema.mail import EmailMessage
from caffeine.common.store.pubsub import PubSubMessage


@pytest.mark.asyncio
async def test_email_job():
    pubsub = Mock()
    email = Mail(hostname="127.0.0.1", port=1025, from_address="email@example.net")
    to = "to_address_{}@example.net".format(secrets.token_hex(5))
    confirm_job = EmailJob(pubsub, email)
    email_msg = EmailMessage(to=to, subject="Test subject")
    msg = PubSubMessage(
        uuid=str(uuid4()),
        data=email_msg.dict(),
        created_at=pendulum.now().int_timestamp,
        updated_at=pendulum.now().int_timestamp,
        channel="test",
    )
    await confirm_job.send_email(msg)
    res = httpx.get("http://127.0.0.1:8025/api/v2/search?kind=to&query={}".format(to))
    data = res.json()
    msg_from_email = data["items"][0]
    assert msg_from_email["Raw"]["From"] == email.from_address
    assert msg_from_email["Raw"]["To"][0] == to
