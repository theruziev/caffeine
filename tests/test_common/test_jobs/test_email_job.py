from uuid import uuid4

import pendulum
import pytest
from async_sender import Mail
from asynctest import MagicMock, Mock, CoroutineMock

from caffeine.common.job.email import EmailJob
from caffeine.common.schema.mail import EmailMessage
from caffeine.common.store.pubsub import PubSubMessage


@pytest.mark.asyncio
async def test_confirm_email_job():
    subscriber = Mock()
    email = CoroutineMock(Mail())

    async def send_email(msg):
        print(msg)

    email.side_effect = send_email

    confirm_job = EmailJob(subscriber, email)
    email_msg = EmailMessage(to="hello@example.com")
    msg = PubSubMessage(
        uuid=str(uuid4()),
        data=email_msg.dict(),
        created_at=pendulum.now().int_timestamp,
        updated_at=pendulum.now().int_timestamp,
        channel="test",
    )

    await confirm_job.send_email(msg)
