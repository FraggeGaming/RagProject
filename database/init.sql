CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS events(id bigserial PRIMARY KEY, embedding vector(768));

