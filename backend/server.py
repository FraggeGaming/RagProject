from datetime import datetime
from flask import Flask, jsonify, request
from pgvector import Vector
import psycopg2
from flask_cors import CORS

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from sentence_transformers import SentenceTransformer, util

from pgvector.psycopg2 import register_vector
from flask import Response


app = Flask(__name__)
CORS(app)

#Init the llm
#Ollama is needed for this, and i chose to use this 0.5b model
    #https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF?local-app=ollama
    #Download it using: ollama run hf.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF:Q4_K_M
llm = ChatOllama(
    model="hf.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF:Q4_K_M",
    temperature=0,
)

model_path = "ibm-granite/granite-embedding-english-r2"
model = SentenceTransformer(model_path)

def GenerateLlmResponse(llm, text):
    prompt = PromptTemplate(
        template=(
            "{text}"
        ),
        input_variables=["text"],
    )

    rag_chain = prompt | llm | StrOutputParser()
    response = rag_chain.invoke({"text": text})
    print(response)
    return response


def fetchSimilarEvents(msg, dates):
    embedding = model.encode(msg)
    if hasattr(embedding, "tolist"):
        embedding = embedding.tolist()
    embedding = Vector(embedding)


    start, end = None, None
    if dates:
        if len(dates) > 0:
            start = dates[0]
        if len(dates) > 1:
            end = dates[1]

    where_clause = ""
    params = []

    if start and end:
        where_clause = "WHERE event_date BETWEEN %s::date AND %s::date"
        params.extend([start, end])
    elif start:
        where_clause = "WHERE event_date = %s::date"
        params.append(start)
    elif end:
        where_clause = "WHERE event_date = %s::date"
        params.append(end)
        
    print("WHERE:", where_clause)
    print("PARAMS:", params, "TYPES:", [type(p) for p in params])
    with psycopg2.connect(
        dbname="rag",
        user="postgres",
        password="",
        host="localhost",
        port=5432
    ) as conn:
        register_vector(conn)
        with conn.cursor() as cur:
            cur.execute(f"""
                SELECT title, full_desc, place, event_date, link
                FROM events
                {where_clause}
                ORDER BY embedding <-> %s
                LIMIT 2;
            """, (*params, embedding))
            results = cur.fetchall()

    return results

@app.route('/fetchAll', methods=['GET'])
def fetch_all():
    try:
        #If only one date is selected, then that date is in Date-Start
        #If range is selected, range is in Date-Start and Date-End
        message = request.headers.get('Message')
        startDate = request.headers.get('Date-Start')
        endDate = request.headers.get('Date-End')
        
        dateList = []
        dateList.append(datetime.fromisoformat(startDate).date())
        if(endDate):
            dateList.append(datetime.fromisoformat(endDate).date())
            
        if len(dateList) == 2:
               
            d1 = dateList[0]
            d2 = dateList[1]

            if d1 and d2 and d1 > d2:
                dateList = [dateList[1], dateList[0]]
            
        vectorStore = fetchSimilarEvents(message, dateList)
        enriched_entries = []

        for title, full_desc, place, event_date, link in vectorStore:
            item_context = f"Title: {title}\nDescription: {full_desc}\nLocation: {place}"
            
            llm_description = GenerateLlmResponse(
                llm,
                f"Provide a concise and engaging description for the following event:\n\n{full_desc}"
            )
            
            enriched_entry = f"{title}\n{llm_description}\n{place}\n{event_date}\n{link}"
            enriched_entries.append(enriched_entry)
            enriched_entries.append("\n--------------------------\n")


        r = "\n\n".join(enriched_entries)
        print(r)
        
        if not r.strip():  
            response = "No events found"
        else:
            response = r

        
        
        return jsonify({"text": response})

    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)



