from sentence_transformers import SentenceTransformer, util
from psycopg2 import connect
from pathlib import Path
from pgvector.psycopg2 import register_vector

init_sql_script = Path("./init.sql").read_text()
sentences = ["The brown fox leaps over the fence", "Animals jumping over stuff", "The bear runs through the parking lot.", "Something else is written here...", "Car parking here.", "A bird flies into a window and dies."]
model_path = "ibm-granite/granite-embedding-english-r2"

with connect(database="rag", user="arthur", password="") as db:
    with db.cursor() as cur:
        model = SentenceTransformer(model_path)
        cur.execute(init_sql_script)
        register_vector(db)
        embeddings = model.encode(sentences)
        for embedding in embeddings:
            print(f"Shape: {embedding.shape}")
            cur.execute(f"INSERT INTO events(embedding) VALUES (%s);", (embedding,))
    db.commit()
    
