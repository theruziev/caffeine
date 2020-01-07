import click
from async_sender import Mail

from caffeine.common.pubsub import PostgresPubSub
from caffeine.common.job.email import EmailJob
from caffeine.common.store.postgresql.db import PostgreSQLDb
from caffeine.common.store.postgresql.pubsub import PubSubStore


@click.command()
@click.option("--dsn", required=True, type=str)
@click.option("--hostname", required=True, type=str)
@click.option("--port", required=True, type=int)
@click.option("--use_tls", is_flag=True)
@click.option("--use_starttls", is_flag=True)
@click.option("--username", type=str)
@click.option("--password", type=str)
@click.option("--from_address", type=str)
async def confirm_email(
    ctx, dsn, hostname, port, use_tls, use_starttls, username, password, from_address
):
    db: PostgreSQLDb = PostgreSQLDb(dsn)
    await db.init()
    try:
        pubsub_store = PubSubStore(db)
        pubsub = PostgresPubSub(pubsub_store)
        subscriber = await pubsub.subscribe("confirm_email")
        email = Mail(
            hostname=hostname,
            port=port,
            use_tls=use_tls,
            use_starttls=use_starttls,
            username=username,
            password=password,
            from_address=from_address or username,
        )

        confirm_job = EmailJob(subscriber, email)
    finally:
        await db.shutdown()
