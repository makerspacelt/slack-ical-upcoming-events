from datetime import datetime, timedelta
from typing import Optional, Union

from pytz import timezone, UTC
from os import environ

import caldav
from twisted.internet import task
from twisted.internet import reactor

UPDATE_INTERVAL_MINUTES = 2

URL = "https://owncloud.inphima.de/remote.php/dav/calendars/fscs/fs-kalenderics/"
USER = environ.get("USER")
PW = environ.get("PW")

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


def events_in_near_future() -> str:
    start = datetime.now(tz=UTC) + timedelta(minutes=15)
    end = start + timedelta(minutes=15+UPDATE_INTERVAL_MINUTES)
    events = calendar.date_search(start=start, end=end)
    return "\n".join([event_description(e) for e in events if start <= e.instance.vevent.dtstart.value < end])


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


def check_for_changes():
    print("check_for_changes")
    new = new_events()
    if new:
        print("New events:\n" + new)
    modified = modified_events()
    if modified:
        print("Modified events:\n" + modified)

    near_future = events_in_near_future()
    if near_future:
        print("Events starting soon:\n" + near_future)
    now = datetime.now()
    if now.weekday() == 0 and now.hour == 7 and now.minute < UPDATE_INTERVAL_MINUTES:
        week = events_of_week()
        if week:
            print("Events this week:\n" + week)
        else:
            print("No Events this week :'(")


check_for_changes()
loop = task.LoopingCall(check_for_changes)
loop.start(UPDATE_INTERVAL_MINUTES * 60)

reactor.run()
