from uuid import uuid4

import pendulum
import pytest
from asynctest import Mock

from caffeine.common.schema.mail import EmailMessage
from caffeine.common.job.email import EmailJob
from caffeine.common.store.pubsub import PubSubMessage


@pytest.mark.asyncio
async def test_confirm_email_job():
    subscriber = Mock()
    email = Mock()

    confirm_job = EmailJob(subscriber, email)
    email_msg = EmailMessage()
    msg = PubSubMessage(
        uuid=str(uuid4()),
        data=email_msg.dict(),
        created_at=pendulum.now(),
        updated_at=pendulum.now(),
        channel="test",
    )

    await confirm_job.send_email(msg)
