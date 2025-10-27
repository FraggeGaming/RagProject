CREATE EXTENSION IF NOT EXISTS vector;

DROP TABLE IF EXISTS events;
CREATE TABLE IF NOT EXISTS events (
    title TEXT NOT NULL,
    id bigserial PRIMARY KEY,
    date_raw TEXT,
    full_desc TEXT,
    duration TEXT,
    place TEXT,
    event_date DATE,
    link TEXT,
    embedding vector(768)
);

