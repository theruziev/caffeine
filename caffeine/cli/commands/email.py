import asyncio

import click
from async_sender import Mail

from caffeine.common.pubsub import PostgresPubSub
from caffeine.common.job.email import EmailJob
from caffeine.common.store.postgresql.db import PostgreSQLDb
from caffeine.common.store.postgresql.pubsub import PubSubStore


async def send_email_job(
    dsn, hostname, port, use_tls, use_starttls, username, password, from_address
):
    db: PostgreSQLDb = PostgreSQLDb(dsn)
    await db.init()
    try:
        pubsub_store = PubSubStore(db)
        pubsub = PostgresPubSub(pubsub_store)
        email = Mail(
            hostname=hostname,
            port=port,
            use_tls=use_tls,
            use_starttls=use_starttls,
            username=username,
            password=password,
            from_address=from_address or username,
        )

        confirm_job = EmailJob(pubsub, email)
        await confirm_job.listen()
    finally:
        await db.shutdown()


@click.command()
@click.option("--dsn", required=True, type=str)
@click.option("--hostname", required=True, type=str)
@click.option("--port", required=True, type=int)
@click.option("--use_tls", is_flag=True)
@click.option("--use_starttls", is_flag=True)
@click.option("--username", type=str)
@click.option("--password", type=str)
@click.option("--from_address", type=str)
def send_email(
    dsn, hostname, use_tls, use_starttls, username, password, from_address, port=1025,
):
    asyncio.run(
        send_email_job(dsn, hostname, port, use_tls, use_starttls, username, password, from_address)
    )
