from datetime import datetime, timedelta

from pytz import UTC

import main
from icalevents import icalevents
from main import event_description, events_of_week, events_in_near_future, new_events, modified_events, get_messages, \
    check_for_changes

ics = b"""
BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
PRODID:-//SabreDAV//SabreDAV//EN
X-WR-CALNAME:FSCS (fscs)
X-APPLE-CALENDAR-COLOR:#748be7
BEGIN:VTIMEZONE
TZID:Europe/Berlin
BEGIN:DAYLIGHT
TZOFFSETFROM:+0100
TZOFFSETTO:+0200
TZNAME:CEST
DTSTART:19700329T020000
RRULE:FREQ=YEARLY;BYDAY=-1SU;BYMONTH=3
END:DAYLIGHT
BEGIN:STANDARD
TZOFFSETFROM:+0200
TZOFFSETTO:+0100
TZNAME:CET
DTSTART:19701025T030000
RRULE:FREQ=YEARLY;BYDAY=-1SU;BYMONTH=10
END:STANDARD
END:VTIMEZONE
BEGIN:VTIMEZONE
TZID:Europe/Rome
BEGIN:DAYLIGHT
TZOFFSETFROM:+0100
TZOFFSETTO:+0200
TZNAME:CEST
DTSTART:19700329T020000
RRULE:FREQ=YEARLY;BYDAY=-1SU;BYMONTH=3
END:DAYLIGHT
BEGIN:STANDARD
TZOFFSETFROM:+0200
TZOFFSETTO:+0100
TZNAME:CET
DTSTART:19701025T030000
RRULE:FREQ=YEARLY;BYDAY=-1SU;BYMONTH=10
END:STANDARD
END:VTIMEZONE

BEGIN:VEVENT
CREATED:20180722T150246Z
LAST-MODIFIED:20180722T150313Z
DTSTAMP:20180722T150313Z
UID:6b6a242f-2041-485f-a527-4579b58a1898
SUMMARY:test1
DTSTART;TZID=Europe/Berlin:20180722T171800
DTEND;TZID=Europe/Berlin:20180722T181800
TRANSP:OPAQUE
LOCATION:here
DESCRIPTION:descript
END:VEVENT

BEGIN:VEVENT
CREATED:20180722T150646Z
LAST-MODIFIED:20180722T152255Z
DTSTAMP:20180722T152255Z
UID:6b6a242f-2041-485f-a527-4579b58a1898
SUMMARY:test2
DTSTART;VALUE=DATE:20180722
DTEND;VALUE=DATE:20180723
TRANSP:TRANSPARENT
X-MOZ-GENERATION:3
SEQUENCE:1
END:VEVENT

BEGIN:VEVENT
CREATED:20180720T233417
DTSTAMP:20180720T233417
LAST-MODIFIED:20180720T233417
UID:XEX87XO0JUC9PXOOV2PHJV
SUMMARY:test3
DTSTART;TZID=Europe/Berlin:20181003T080000
DTEND;TZID=Europe/Berlin:20181004T070000
END:VEVENT

BEGIN:VEVENT
CREATED:20180720T233313Z
LAST-MODIFIED:20180722T150231Z
DTSTAMP:20180722T150231Z
UID:YHCGROTP9ZYFY38UQSX8P
SUMMARY:test4
DTSTART;VALUE=DATE:20181003
DTEND;VALUE=DATE:20181004
TRANSP:TRANSPARENT
X-MOZ-GENERATION:4
END:VEVENT

BEGIN:VEVENT
CREATED:20180719T081515Z
LAST-MODIFIED:20180719T081605Z
DTSTAMP:20180719T081605Z
UID:fa4bcabc-2296-4aac-8bdc-5526a00f348f
SUMMARY:Stammtisch
RRULE:FREQ=MONTHLY;UNTIL=20181106T180000Z;BYDAY=1TU
DTSTART;TZID=Europe/Berlin:20180807T190000
DTEND;TZID=Europe/Berlin:20180807T230000
TRANSP:OPAQUE
LOCATION:Kneipe
SEQUENCE:1
X-MOZ-GENERATION:1
END:VEVENT

BEGIN:VEVENT
CREATED:20180822T150646Z
LAST-MODIFIED:20180822T152255Z
DTSTAMP:20180822T152255Z
UID:6b6a242f-2041-485f-a527-4579b58a1898
SUMMARY:allday 2nd day
DTSTART;VALUE=DATE:20180822
DTEND;VALUE=DATE:20180824
TRANSP:TRANSPARENT
X-MOZ-GENERATION:3
SEQUENCE:1
END:VEVENT

BEGIN:VEVENT
CREATED:20181009T194528Z
LAST-MODIFIED:20181009T194625Z
DTSTAMP:20181009T194625Z
UID:30b2ee53-053b-4ea3-8d73-1edc8f65f87e
SUMMARY:FSVK
RRULE:FREQ=WEEKLY;UNTIL=20181218T171500Z;INTERVAL=2;BYDAY=TU
DTSTART;TZID=Europe/Berlin:20181016T181500
DTEND;TZID=Europe/Berlin:20181016T201500
TRANSP:OPAQUE
END:VEVENT

BEGIN:VEVENT
CREATED:20131009T194625Z
DTSTAMP:20130722T150231Z
UID:YHCGROTP9ZYFY38UQSX8P
SUMMARY:test4
DTSTART;VALUE=DATE:20131003
DTEND;VALUE=DATE:20131004
TRANSP:TRANSPARENT
X-MOZ-GENERATION:4
END:VEVENT

BEGIN:VEVENT
DTSTAMP:20130722T150231Z
UID:YHCGROTP9ZYFY38UQSX8P
SUMMARY:test6
DTSTART;VALUE=DATE:20131103
DTEND;VALUE=DATE:20131104
TRANSP:TRANSPARENT
END:VEVENT

BEGIN:VEVENT
DTSTAMP:20130722T150231Z
UID:YHCGROTP9ZYFY38UQSX8P
SUMMARY:test7 im Timeframe aber ohne created und modified
DTSTART;VALUE=DATE:20201103
DTEND;VALUE=DATE:20201104
TRANSP:TRANSPARENT
END:VEVENT

BEGIN:VEVENT
CREATED:20190207T092257Z
LAST-MODIFIED:20190207T092342Z
DTSTAMP:20190207T092342Z
UID:047ae3bb-7e00-41c9-8cba-9c481529548d
SUMMARY:Sitzung
RRULE:FREQ=WEEKLY;UNTIL=20190402T121000Z;INTERVAL=2
DTSTART;TZID=Europe/Berlin:20190212T141000
DTEND;TZID=Europe/Berlin:20190212T151000
TRANSP:OPAQUE
LOCATION:25.12.O1.51
END:VEVENT

END:VCALENDAR
"""

events = icalevents.events(
    string_content=ics,
    start=datetime(2018, 7, 1) - timedelta(days=365),
    end=datetime(2018, 7, 1) + timedelta(days=3 * 365)
)


def test_event_description_with_datetime_and_location():
    description = event_description(events[0])
    assert "here" in description
    assert "test1" in description
    assert "22.07.2018" in description
    assert "17:18" in description
    assert "18:18" in description


def test_all_day_event_description_without_location():
    description = event_description(events[1])
    assert "test2" in description
    assert "<no location>" in description
    assert "22.07.2018" in description
    assert "23.07.2018" not in description
    assert "00" not in description


def test_event_description_end_same_day():
    description = event_description(events[0])
    assert description.count("22.07.2018") == 1
    assert "17:18" in description
    assert "18:18" in description


def test_event_description_end_next_day():
    description = event_description(events[2])
    assert "03.10.2018" in description
    assert "04.10.2018" in description
    assert "8:00" in description
    assert "7:00" in description


def test_all_day_event_description_end_next_day():
    description = event_description(events[8])
    assert "allday 2nd day" in description
    assert "22.08.2018" in description
    assert "23.08.2018" in description
    assert "24.08.2018" not in description
    assert "00" not in description


def test_events_of_week():
    week = events_of_week(events, datetime(2018, 7, 16, 8, 0, tzinfo=UTC))
    assert [e.summary for e in week] == ["test1", "test2"]


def test_events_in_near_future():
    future = events_in_near_future(events, datetime(2018, 10, 3, 5, 44, 33, tzinfo=UTC))
    assert len(future) == 1
    assert future[0].summary == "test3"


def test_no_events_in_near_future():
    assert len(events_in_near_future(events, datetime(2018, 10, 3, 5, 42, 33, tzinfo=UTC))) == 0
    assert len(events_in_near_future(events, datetime(2018, 10, 3, 5, 43, 33, tzinfo=UTC))) == 1
    assert len(events_in_near_future(events, datetime(2018, 10, 3, 5, 44, 33, tzinfo=UTC))) == 1
    assert len(events_in_near_future(events, datetime(2018, 10, 3, 5, 45, 33, tzinfo=UTC))) == 0


def test_new_events():
    new = new_events(events, datetime(2018, 7, 22, 15, 3, tzinfo=UTC))
    assert len(new) == 1
    assert new[0].summary == "test1"


def test_no_new_events():
    assert len(new_events(events, datetime(2018, 7, 22, 15, 2, tzinfo=UTC))) == 0
    assert len(new_events(events, datetime(2018, 7, 22, 15, 3, tzinfo=UTC))) == 1
    assert len(new_events(events, datetime(2018, 7, 22, 15, 4, tzinfo=UTC))) == 1
    assert len(new_events(events, datetime(2018, 7, 22, 15, 5, tzinfo=UTC))) == 0


def test_new_events_ignore_uids():
    new = new_events(events, datetime(2018, 7, 22, 15, 3, tzinfo=UTC), ignore_uids=None)
    assert len(new) == 1
    new_with_ignore = new_events(events, datetime(2018, 7, 22, 15, 3, tzinfo=UTC), ignore_uids=new[0].uid)
    assert len(new_with_ignore) == 0


def test_modified_events():
    future = modified_events(events, datetime(2018, 7, 22, 15, 3, tzinfo=UTC))
    assert len(future) == 1
    assert future[0].summary == "test4"


def test_new_event_is_not_modified():
    future = new_events(events, datetime(2018, 7, 20, 21, 35, tzinfo=UTC))
    assert len(future) == 1
    assert future[0].summary == "test3"
    assert len(modified_events(events, datetime(2018, 7, 20, 21, 35, tzinfo=UTC))) == 0


def test_get_messages_events_this_week():
    messages = get_messages(events, datetime(2018, 7, 16, 7, 0, 42, tzinfo=UTC))
    assert len(messages) == 1
    assert "test1" in messages[0]["text"]
    assert "here" in messages[0]["text"]
    assert "test2" in messages[0]["text"]


def test_get_messages_events_this_week_recurring():
    messages = get_messages(events, datetime(2018, 10, 1, 7, 0, 42, tzinfo=UTC))
    assert len(messages) == 1
    assert "test3" in messages[0]["text"]
    assert "test4" in messages[0]["text"]
    assert "Stammtisch" in messages[0]["text"]
    assert "02.10." in messages[0]["text"]
    assert "19:00" in messages[0]["text"]


def test_date_of_tuesday_recurring_utc_plus_1_time():
    description = event_description(events[7])
    assert "06.11.2018" in description
    assert "19:00" in description


def test_biweekly_event():
    week_start = events_of_week(events, datetime(2018, 10, 15, 8, 0, tzinfo=UTC))
    week_middle_not_included = events_of_week(events, datetime(2018, 10, 22, 8, 0, tzinfo=UTC))
    week_middle_included = events_of_week(events, datetime(2018, 10, 29, 8, 0, tzinfo=UTC))
    week_last = events_of_week(events, datetime(2018, 12, 10, 8, 0, tzinfo=UTC))
    week_after_last = events_of_week(events, datetime(2018, 12, 17, 8, 0, tzinfo=UTC))
    assert [e.summary for [e] in [week_start, week_middle_included, week_last]] == ["FSVK"] * 3
    assert len(week_start +  week_middle_included + week_last) == 3
    assert len(week_middle_not_included + week_after_last) == 0
    assert "18:15" in event_description(week_start[0])
    assert "18:15" in event_description(week_last[0])


def test_biweekly_event_not_by_day():
    week_start = events_of_week(events, datetime(2019, 2, 11, 8, 0, tzinfo=UTC))
    week_middle_not_included = events_of_week(events, datetime(2019, 2, 18, 8, 0, tzinfo=UTC))
    week_middle_included = events_of_week(events, datetime(2019, 2, 26, 8, 0, tzinfo=UTC))
    week_last = events_of_week(events, datetime(2019, 3, 26, 8, 0, tzinfo=UTC))
    week_after_last = events_of_week(events, datetime(2019, 4, 1, 8, 0, tzinfo=UTC))
    assert [e.summary for [e] in [week_start, week_middle_included, week_last]] == ["Sitzung"] * 3
    assert len(week_start + week_middle_included + week_last) == 3
    assert len(week_middle_not_included + week_after_last) == 0
    assert "14:10" in event_description(week_start[0])
    assert "14:10" in event_description(week_last[0])


def test_check_for_changes_does_not_crash():
    main.URLS = ["http://example.test"]
    assert check_for_changes() is None
