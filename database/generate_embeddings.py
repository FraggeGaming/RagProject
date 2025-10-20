from sentence_transformers import SentenceTransformer, util
from psycopg2 import connect
from pathlib import Path
from pgvector.psycopg2 import register_vector
from datetime import datetime, date, time, tzinfo, timezone
# from dateutil import parser as date_parser
import json
import re

# Currently only extracts the first time. TODO: two dates and times
# Maybe two patterns
extract_duration_pattern = re.compile(r"(?:(?:\s|\w)*)(?P<t1>[0-9][0-9]:[0-9][0-9])(?:(?:\s|\w)*)(?P<t2>[0-9][0-9]:[0-9][0-9])")
duration_multi_day_pat = re.compile(r"(?P<d1>[0-9][0-9]?) (?P<m1>[a-z]+) kl\. (?P<t1>[0-9][0-9]:[0-9][0-9]) till (?P<d2>[0-9][0-9]?) (?P<m2>[a-z]+) kl\. (?P<t2>[0-9][0-9]:[0-9][0-9])")
duration_single_day_pat = re.compile(r"(?P<t1>[0-9][0-9]:[0-9][0-9]) - (?P<t2>[0-9][0-9]:[0-9][0-9])")
date_pat = re.compile(r"[a-z]+ (?P<d>[0-9]+) (?P<m>[A-Z]+)")
init_sql_script = Path("./init.sql").read_text()
model_path = "ibm-granite/granite-embedding-english-r2"
input_path = "../Scraper/events.json"

def _parse_date(raw_date):
    """Parses a date from the Date field. Returns a python date object."""
    date_match = date_pat.match(raw_date)
    if date_match == None:
        return None

    day = int(date_match.group("d"))
    raw_month = date_match.group("m")
    month = 0
    if raw_month == "JAN":
        month = 1
    elif raw_month == "FEB":
        month = 2
    elif raw_month == "MAR":
        month = 3
    elif raw_month == "APR":
        month = 4
    elif raw_month == "MAY":
        month = 5
    elif raw_month == "JUN":
        month = 6
    elif raw_month == "JUL":
        month = 7
    elif raw_month == "AUG":
        month = 8
    elif raw_month == "SEP":
        month = 9
    elif raw_month == "OKT":
        month = 10
    elif raw_month == "NOV":
        month = 11
    elif raw_month == "DEC":
        month = 12
    else:
        raise ValueError(f"Bad month spec: {raw_month}")

    return date(date.today().year, month, day)

# TODO time
def _process_multi_day_date_spec(day, month, time):
    """
    Turns three strings for day, month and time captured from the scrape into
    a datetime.
    """

    time = date_parser.parse(time)
    
    day = int(day)
    month = 0
    if month == "januari":
        month = 1
    elif month == "februari":
        month = 2
    elif month == "mars":
        month = 3
    elif month == "april":
        month = 4
    elif month == "maj":
        month = 5
    elif month == "juni":
        month = 6
    elif month == "juli":
        month = 7
    elif month == "augusti":
        month = 8
    elif month == "september":
        month = 9
    elif month == "oktober":
        month = 10
    elif month == "november":
        month = 11
    elif month == "december":
        month = 12
    else:
        raise ValueError(f"Bad month in multi day event: {month}")

    return datetime(datetime.now(None).year, month, day, time.hour, time.minute)

def _parse_duration(raw_duration, raw_date):
    """
    Takes a raw duration from the scraped website data and turns it into a python duration.
    Returns a tuple of start date, end date and duration. All of these are datetimes.
    """
    multi_day_match = duration_multi_day_pat.match(raw_duration)
    if multi_day_match == None:
        single_day_match = duration_single_day_pat.match(raw_duration)
        
        start_time_raw = single_day_match.group("t1")
        end_time_raw = single_day_match.group("t2")
        
        start_time = date_parser.parse(start_time_raw)
        end_time = date_parser.parse(end_time_raw)
        
        date = _parse_date(raw_date)
        
        # TODO fix timezone to local stuff
        start_datetime = datetime(date.year, date.month, date.day, start_time.hour, start_time.minute)
        end_datetime = datetime(date.year, date.month, date.day, end_time.hour, end_time.minute)
        end_datetime = datetime.combine(date, end_time, timezone.utc)
        return (start_datetime, end_datetime, end_datetime - start_datetime)
    else:
        start_day = multi_day_match.group("d1")
        start_month_raw = multi_day_match.group("m1")
        start_time = multi_day_match.group("t1")

        start_datetime = _process_multi_day_date_spec(start_day, start_month_raw)

        end_day = multi_day_match.group("d2")
        end_month_raw = multi_day_match.group("m2")
        end_time = multi_day_match.group("t2")

        end_datetime = _process_multi_day_date_spec(end_day, end_month_raw, end_time)

        return (start_datetime, end_datetime, end_datetime - start_datetime)
    

class EventEntry:

    def __init__(self, json_object, embedding):
        self.title = json_object["Title"]
        self.date_raw = json_object["Date"]
        self.full_desc = json_object["Full description"]
        self.time_span_raw = json_object["Duration"]
        self.place = json_object["Plats"]
        self.embedding = embedding

    def insert(self, cursor):
        cursor.execute("INSERT INTO events(title, embedding) VALUES (%s, %s);", (self.title, self.embedding))


def init_db(connection):
    """Initializes the database with our schema. Note: currently drops the existing table.
    """
    with connection.cursor() as cursor:
        cursor.execute(init_sql_script);

def load_scraped_events(model, max=0):
    """Loads events from json scrape and computes embeddings. Returns a list of EventEntry objects."""
    scrape = None
    with open(input_path) as file:
        scrape = json.load(file)

    full_descriptions = []
    count = 0
    for object in scrape:
        full_descriptions.append(object["Full description"])
        count += 1
        if max > 0 and count > max:
            break

    embeddings = model.encode(full_descriptions)

    events = []
    for (object, embedding) in zip(scrape,embeddings):
        events.append(EventEntry(object, embedding))

    return events
        

def insert_events(connection, events):
    """Insert events list into database."""
    with connection.cursor() as cursor:
        for e in events:
            e.insert(cursor)

def main():

    model = SentenceTransformer(model_path)

    print("Generated events")
    with connect(dbname="rag", user="arthur") as connection:
        register_vector(connection)
        init_db(connection)
        events = load_scraped_events(model, max=10)
        insert_events(connection, events)


if __name__ == "__main__":
    main()
