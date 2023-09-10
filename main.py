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

# when to send week/day event list, in UTC
UPDATE_WEEK_AT_HOUR = 12
UPDATE_DAY_AT_HOUR = 8

UPDATE_INTERVAL_MINUTES = 2

TZ = timezone('Europe/Vilnius')
URLS = environ.get("CALENDAR_URLS", "").split(", ")
WEBHOOK_URL = environ.get("WEBHOOK_URL")
WEBHOOK_ERROR_URL = environ.get("WEBHOOK_ERROR_URL")


def date_as_string(date: Union[datetime, date]) -> str:
    return date.strftime("%Y-%m-%d")


def datetime_as_string(date: datetime) -> str:
    return date.strftime("%Y-%m-%d %H:%M")


def time_as_string(date: datetime) -> str:
    return date.strftime("%H:%M")


def event_description(event: Event) -> str:
    start = event.start.astimezone(TZ)  # type: datetime
    end = event.end.astimezone(TZ)  # type: datetime
    summary = event.summary  # type: str
    location = event.location  # type: Optional[str]
    if location is None:
        location = ""
    else:
        location = f" at {location}"

    start_fmt = date_as_string(start)

    if event.all_day:
        end_day = end.date() - timedelta(days=1)
        if start.date() == end_day:
            start_fmt = date_as_string(start)
            return f"*{summary}* {start_fmt}{location}"
        start_fmt = date_as_string(start)
        end_fmt = date_as_string(end_day)
        return f"*{summary}* from {start_fmt} to {end_fmt}{location}"
    else:
        if start.date() == end.date():
            start_fmt = datetime_as_string(start)
            end_fmt = time_as_string(end)
            return f"*{summary}* from {start_fmt} to {end_fmt}{location}"
        start_fmt = datetime_as_string(start)
        end_fmt = time_as_string(end)
        return f"*{summary}* from {start_fmt} to {end_fmt}{location}"


def to_datetime(d: Optional[Union[datetime, date]]) -> datetime:
    if d is None:
        return datetime(1970, 1, 1, tzinfo=UTC)
    if isinstance(d, datetime):
        return d
    return datetime.combine(d, time(0, 0, tzinfo=UTC))

def events_of_day(events: [Event], now: datetime) -> [Event]:
    start = now
    end = start.replace(hour=23, minute=59, second=59)
    return [e for e in events if start <= to_datetime(e.start) < end]

def events_of_week(events: [Event], now: datetime) -> [Event]:
    start = now
    end = start + timedelta(days=7)
    return [e for e in events if start <= to_datetime(e.start) < end]


def get_message(msg: str, events: [Event]) -> dict:
    events_fmt = "• " + "\n• ".join([event_description(e) for e in events])
    return {"text": "\n".join((msg, events_fmt))}


def get_messages(events, now, force_send_week=False, force_send_day=False):
    messages = []

    send_week = now.weekday() == 0 and \
        now.hour == UPDATE_WEEK_AT_HOUR and \
        now.minute < UPDATE_INTERVAL_MINUTES
    send_day = now.weekday() > 0 and \
        now.hour == UPDATE_DAY_AT_HOUR and \
        now.minute < UPDATE_INTERVAL_MINUTES
    if force_send_week or send_week:
        week = events_of_week(events, now)
        if len(week) > 0:
            messages.append(get_message("Events this week:", week))
        else:
            messages.append(get_message("No events this week 😢", []))
    elif force_send_day or send_day:
        day = events_of_day(events, now)
        if len(day) > 0:
            messages.append(get_message("Events today:", day))

    return messages


def post_message(msg: dict):
    logging.info("posting message %s" % msg)
    requests.post(WEBHOOK_URL, json=msg)


def post_error_message(msg: dict):
    logging.info("posting error message %s" % msg)
    requests.post(WEBHOOK_ERROR_URL, json=msg)


def get_events(now: datetime) -> [Event]:
    return sorted([event
                   for url in URLS
                   for event in icalevents.events(url,
                                                  start=now - timedelta(days=365),
                                                  end=now + timedelta(days=3 * 365))])


def check_for_changes():
    logging.info("checking for changes")

    try:
        now = datetime.now(tz=UTC)

        events = get_events(now)
        messages = get_messages(events, now, force_send_day=False, force_send_week=False)
        for message in messages:
            post_message(message)

        logging.info("checking for changes done, %d events found" % len(events))
    except Exception as e:
        logging.error(str(e))
        try:
            post_error_message(get_message("Sorry, there was an error 🤯.\n%s" % str(e), []))
        except Exception as e:
            logging.error("WTF: " + str(e))


def error_handler(error: Failure):
    logging.error(error)
    post_error_message(get_message("Sorry, there was an error 🤯. I will kill myself 🔫.\n%s" % str(error.value), []))


def main():
    logging.basicConfig(format='%(process)d %(asctime)s %(levelname)s: %(message)s',
                        level=logging.INFO, stream=sys.stdout)

    loop = task.LoopingCall(check_for_changes)
    deferred = loop.start(UPDATE_INTERVAL_MINUTES * 60)
    deferred.addErrback(error_handler)

    reactor.run()

def test(publish=False):
    now = datetime.now(tz=UTC)

    events = get_events(now)
    messages = get_messages(events, now, force_send_week=True)
    for message in messages:
        print(message)
    messages = get_messages(events, now, force_send_day=True)
    for message in messages:
        if publish:
            post_message(message)
        else:
            print(message)


if __name__ == '__main__':
    action = len(sys.argv) > 1 and sys.argv[1] or 'production'
    if action == 'test-print':
        test()
    elif action == 'test-send':
        test(publish=True)
    elif action == 'production':
        main()
    else:
        print(f'usage: {sys.argv[0]} [production|test-print|test-send]')
