from sentence_transformers import SentenceTransformer, util
from psycopg2 import connect
from pathlib import Path
from pgvector.psycopg2 import register_vector
from datetime import datetime
import json
import re

# Currently only extracts the first time. TODO: two dates and times
# Maybe two patterns
extract_duration_pattern = re.compile(r"(?:(?:\s|\w)*)([0-9][0-9]:[0-9][0-9])")

def parse_duration(raw_duration):
    

# Takes
def process_date(raw_date):
    pass

class EventEntry:

    def __init__(self, json_object, embedding):
        self.title = json_object["Title"]
        self.date_raw = json_object["Date"]
        self.full_desc = json_object["Full description"]
        self.time_span_raw = json_object[""]
        self.embedding = embedding

    def insert(self, cursor):
        cursor.execute("INSERT INTO events(title, embedding) VALUES (%s, %s);", self.title, self.embedding)
        

init_sql_script = Path("./init.sql").read_text()
sentences = ["The brown fox leaps over the fence", "Animals jumping over stuff", "The bear runs through the parking lot.", "Something else is written here...", "Car parking here.", "A bird flies into a window and dies."]
model_path = "ibm-granite/granite-embedding-english-r2"
input_path = "../Scraper/events.json"

scrape = None

with open(input_path) as file:
    scrape = json.load(file)

full_descriptions = []
events = []

for object in scrape:
    full_descriptions.append(object["Full description"])

print("Generated total descriptions array.")

model = SentenceTransformer(model_path)
embeddings = model.encode(full_descriptions)

print("Generated embeddings.")

for (object, embedding) in zip(scrape, embeddings):
    events.append(EventEntry(object, embedding))

print("Generated events")

with connect(database="rag", user="arthur", password="") as db:
    with db.cursor() as cur:
        cur.execute(init_sql_script)
        register_vector(db)
        for e in events:
            e.insert(cur)
    db.commit()
