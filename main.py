import logging
import sys
from datetime import datetime, timedelta, date, time
from os import environ
from typing import Union, Optional

import requests
from pytz import timezone, UTC
from twisted.internet import reactor
from twisted.internet import task
from twisted.python.failure import Failure

import icalevents.icalevents as icalevents
from icalevents.icalparser import Event

UPDATE_INTERVAL_MINUTES = 2

URLS = environ.get("CALENDAR_URLS", "").split(", ")
WEBHOOK_URL = environ.get("WEBHOOK_URL")


def date_as_string(date: datetime) -> str:
    return date.strftime("%d.%m.%Y")


def datetime_as_string(date: datetime) -> str:
    return date.astimezone(timezone('Europe/Berlin')).strftime("%d.%m.%Y %H:%M")


def time_as_string(date: datetime) -> str:
    return date.astimezone(timezone('Europe/Berlin')).strftime("%H:%M")


def event_description(event: Event) -> str:
    start = event.start  # type: datetime
    end = event.end  # type: datetime
    summary = event.summary  # type: str
    location = event.location  # type: Optional[str]
    if location is None:
        location = "<no location>"
    if event.all_day:
        end_day = end.date() - timedelta(days=1)
        if start.date() == end_day:
            return "*%s* %s at %s" % (summary, date_as_string(start), location)
        return "*%s* from %s to %s at %s" % (summary, date_as_string(start), date_as_string(end_day), location)
    else:
        if start.date() == end.date():
            return "*%s* from %s to %s at %s" % (summary, datetime_as_string(start), time_as_string(end), location)
        return "*%s* from %s to %s at %s" % (summary, datetime_as_string(start), datetime_as_string(end), location)


def to_datetime(d: Union[datetime, date]) -> datetime:
    if isinstance(d, datetime):
        return d
    return datetime.combine(d, time(0, 0, tzinfo=UTC))


def events_of_week(events: [Event], now: datetime) -> [Event]:
    start = now
    end = start + timedelta(days=7)
    return [e for e in events if start <= to_datetime(e.start) < end]


def events_in_near_future(events: [Event], now: datetime) -> [Event]:
    start = now + timedelta(minutes=15)
    end = start + timedelta(minutes=UPDATE_INTERVAL_MINUTES)
    return [e for e in events if start <= to_datetime(e.start) < end]


def new_events(events: [Event], now: datetime) -> [Event]:
    start = now - timedelta(minutes=UPDATE_INTERVAL_MINUTES)
    end = now
    return [e for e in events if start <= to_datetime(e.created) < end]


def modified_events(events: [Event], now: datetime) -> [Event]:
    start = now - timedelta(minutes=UPDATE_INTERVAL_MINUTES)
    end = now
    return [e for e in events if start <= to_datetime(e.last_modified) < end
            and not(start <= to_datetime(e.created) < end)]


def get_message(msg: str, events: [Event]) -> dict:
    return {"text": msg + "\n" + "\n".join([event_description(e) for e in events])}


def get_messages(events, now):
    messages = []
    new = new_events(events, now)
    if len(new) > 0:
        messages.append(get_message("New event:", new))

    modified = modified_events(events, now)
    if len(modified) > 0:
        messages.append(get_message("Modified event:", modified))

    near_future = events_in_near_future(events, now)
    if len(near_future) > 0:
        messages.append(get_message("Event starting soon:", near_future))

    if now.weekday() == 0 and now.hour == 7 and now.minute < UPDATE_INTERVAL_MINUTES:
        week = events_of_week(events, now)
        if len(week) > 0:
            messages.append(get_message("Events this week:", week))
        else:
            messages.append(get_message("No events this week 😢", []))

    return messages


def post_message(msg: dict):
    logging.info("posting message %s" % msg)
    requests.post(WEBHOOK_URL, json=msg)


def check_for_changes():
    logging.info("checking for changes")

    now = datetime.now(tz=UTC)

    events = sorted([event
                     for url in URLS
                     for event in icalevents.events(url,
                                                    start=now - timedelta(days=365),
                                                    end=now + timedelta(days=3 * 365))])

    messages = get_messages(events, now)

    for message in messages:
        post_message(message)

    logging.info("checking for changes done")


def error_handler(error: Failure):
    logging.error(error)
    post_message(get_message("Sorry, there was an error 🤯. I will kill myself 🔫.\n%s" % str(error.value), []))


def main():
    logging.basicConfig(format='%(process)d %(asctime)s %(levelname)s: %(message)s',
                        level=logging.INFO, stream=sys.stdout)

    loop = task.LoopingCall(check_for_changes)
    deferred = loop.start(UPDATE_INTERVAL_MINUTES * 60)
    deferred.addErrback(error_handler)

    reactor.run()


if __name__ == '__main__':
    main()
