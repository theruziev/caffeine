import asyncio

from aio_pubsub.interfaces import PubSub
from async_sender import Mail, Message, Attachment

from caffeine.common.abc.job import BaseJob
from caffeine.common.logger import logger
from caffeine.common.schema.mail import EmailMessage
from caffeine.common.store.pubsub import PubSubMessage


class EmailJob(BaseJob):
    def __init__(self, pubsub: PubSub, email: Mail):
        self.pubsub = pubsub
        self.email = email

    async def send_email(self, msg: PubSubMessage) -> None:

        email = EmailMessage(**msg.data)

        email_raw = Message(
            subject=email.subject,
            to=email.to,
            body=email.body,
            html=email.html,
            from_address=email.from_address or self.email.from_address,
            cc=email.cc,
            bcc=email.bcc,
            reply_to=email.reply_to,
            date=email.date,
        )

        for attachment in email.attachments:
            email_raw.attach(
                Attachment(
                    filename=attachment.filename,
                    content_type=attachment.content_type,
                    data=attachment.data,
                )
            )

        await self.email.send(email_raw)

    async def listen(self):
        subscriber = await self.pubsub.subscribe("emails")
        while True:
            async for msg in subscriber:
                try:
                    logger.debug(msg.dict())
                    await self.send_email(msg)
                    logger.debug("Message successful sent")
                    await asyncio.sleep(0.1)
                except Exception as e:
                    logger.error("{}: {}".format(str(e), msg.dict()))
                    await self.pubsub.publish("emails", msg.data)
            await asyncio.sleep(0.5)
