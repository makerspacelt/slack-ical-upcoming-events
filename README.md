Simple Slack app which triggers a webhook when
* a calender event is created
* a calender event is modified (disabled)
* a calender event starts in around 15 minutes
* a new week starts (summary of upcoming events)

This app supports iCalendar (iCal, ics) files, which can be created by many CalDAV servers like ownCloud or nextcloud.

Note that the timezone Europe/Berlin is hardcoded in some places.

## Configuration

Create a file `.env`:

```
CALENDAR_URLS=https://...ics, https://...ics
WEBHOOK_URL=https://hooks.slack.com/services/...
WEBHOOK_ERROR_URL=https://hooks.slack.com/services/...
```
