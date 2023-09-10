Simple Slack app which posts upcoming events using webhooks
* for the whole week every Monday
* for this day every day except Monday

This app supports iCalendar (iCal, ics) files, which can be created by many CalDAV servers like ownCloud or nextcloud.

## Configuration

Create a file `.env`:

```
CALENDAR_URLS=https://...ics, https://...ics
WEBHOOK_URL=https://hooks.slack.com/services/...
WEBHOOK_ERROR_URL=https://hooks.slack.com/services/...
```

Run with docker-compose:
```shell
docker-compose up
```

## Testing

```shell
# Setup Python virtual environment
python -m venv venv
. ./venv/bin/activate
pip install -r requirements.txt

# Setup env
export CALENDAR_URLS=https://...ics
export WEBHOOK_URL=https://hooks.slack.com/services/...
export WEBHOOK_ERROR_URL=https://hooks.slack.com/services/...

# Run locally
. ./venv/bin/activate
# print next week's & today's event to console
python main.py test-print
# send next week's & today's event to slack
python main.py test-send
# check calendar periodically and send week's events on Monday and day's events every day
python main.py
```

