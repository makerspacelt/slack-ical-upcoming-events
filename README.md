Simple Slack app which triggers a webhook when
* a calender event is created
* a calender event is modified
* a calender event starts in around 15 minutes
* a new week starts (summary of upcoming events)

This app supports iCalendar (iCal, ics) files, which can be created by many CalDAV servers like ownCloud.

## Configuration

Create a file `.env`:

```
CALENDAR_URLS=https://...ics, https://...ics
WEBHOOK_URL=https://hooks.slack.com/services/...
```
