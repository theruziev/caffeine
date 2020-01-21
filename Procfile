web: uvicorn caffeine.rest.app:app --port $PORT --host 0.0.0.0
send-email: ./scripts/cli send-email --dsn $DB_DSN --hostname $MAIL_SERVER --port $MAIL_PORT --from_address $MAIL_USERNAME --username $MAIL_USERNAME --password $MAIL_PASSWORD --use_starttls $MAIL_USESTARTTLS
