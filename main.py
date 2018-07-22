import logging
import sys
from datetime import datetime, timedelta, date, time
from os import environ
from typing import Optional, Union

import caldav
from pytz import timezone, UTC
from twisted.internet import reactor
from twisted.internet import task
from twisted.python.failure import Failure

UPDATE_INTERVAL_MINUTES = 2

URL = "https://owncloud.inphima.de/remote.php/dav/calendars/fscs/fs-kalenderics/"
USER = environ.get("USER")
PW = environ.get("PW")
WEBHOOK_URL = environ.get("WEBHOOK_URL")

calendar = caldav.Calendar(client=caldav.DAVClient(url=URL, username=USER, password=PW), url=URL)


def date_as_string(date: Union[datetime.date, datetime]) -> str:
    if isinstance(date, datetime):
        return date.astimezone(timezone('Europe/Berlin')).strftime("%d.%m.%Y %H:%M")
    return date.strftime("%d.%m.%Y")


def event_description(event: caldav.Event) -> str:
    start = event.instance.vevent.dtstart.value  # type: datetime
    end = event.instance.vevent.dtend.value  # type: datetime
    try:
        summary = event.instance.vevent.summary.value  # type: str
    except AttributeError:
        summary = "<no summary>"
    try:
        location = event.instance.vevent.location.value  # type: str
    except AttributeError:
        location = "<no location>"
    return "%s from %s to %s in %s" % (summary, date_as_string(start), date_as_string(end), location)


def events_of_week() -> str:
    start = datetime.now(tz=UTC)
    end = start + timedelta(days=7)
    events = calendar.date_search(start=start, end=end)
    return "\n".join([event_description(e) for e in events])


def to_datetime(d: Union[datetime, date]) -> datetime:
    if isinstance(d, date):
        return datetime.combine(d, time(0, 0, tzinfo=UTC))
    return d


def events_in_near_future() -> str:
    start = datetime.now(tz=UTC) + timedelta(minutes=15)
    end = start + timedelta(minutes=15+UPDATE_INTERVAL_MINUTES)
    events = calendar.date_search(start=start, end=end)
    return "\n".join([event_description(e) for e in events
                      if start <= to_datetime(e.instance.vevent.dtstart.value) < end])


def new_events() -> Optional[str]:
    start = datetime.now(tz=UTC) - timedelta(days=365)
    end = start + timedelta(days=2 * 365)
    events = calendar.date_search(start=start, end=end)
    threshold = datetime.now(tz=UTC) - timedelta(minutes=UPDATE_INTERVAL_MINUTES)
    new = [e for e in events if e.instance.vevent.created.value >= threshold]
    if len(new) == 0:
        return None
    return "\n".join([event_description(e) for e in new])


def modified_events() -> Optional[str]:
    start = datetime.now(tz=UTC) - timedelta(days=365)
    end = start + timedelta(days=2 * 365)
    events = calendar.date_search(start=start, end=end)
    threshold = datetime.now(tz=UTC) - timedelta(minutes=UPDATE_INTERVAL_MINUTES)
    modified = [e for e in events
                if e.instance.vevent.last_modified.value >= threshold > e.instance.vevent.created.value]
    if len(modified) == 0:
        return None
    return "\n".join([event_description(e) for e in modified])


def post_message(msg: str):
    json = {"text": msg}
    logging.info("posting message %s" % json)
    # requests.post(WEBHOOK_URL, json=json)


def check_for_changes():
    logging.info("checking for changes")
    new = new_events()
    if new:
        post_message("New events:\n" + new)
    modified = modified_events()
    if modified:
        post_message("Modified events:\n" + modified)

    near_future = events_in_near_future()
    if near_future:
        post_message("Events starting soon:\n" + near_future)
    now = datetime.now()
    if now.weekday() == 0 and now.hour == 7 and now.minute < UPDATE_INTERVAL_MINUTES:
        week = events_of_week()
        if week:
            post_message("Events this week:\n" + week)
        else:
            post_message("No Events this week :'(")


def error_handler(error: Failure):
    logging.error(error)
    post_message("Sorry, there was an error 🤯. I will kill myself 🔫.\n%s" % str(error.value))


def main():
    logging.basicConfig(format='%(process)d %(asctime)s %(levelname)s: %(message)s',
                        level=logging.INFO, stream=sys.stdout)

    loop = task.LoopingCall(check_for_changes)
    deferred = loop.start(UPDATE_INTERVAL_MINUTES * 60)
    deferred.addErrback(error_handler)

    reactor.run()


if __name__ == '__main__':
    main()
