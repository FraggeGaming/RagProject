from flask import Flask, jsonify, request
import psycopg2
from flask_cors import CORS

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from sentence_transformers import SentenceTransformer, util

from pgvector.psycopg2 import register_vector


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

def GenerateLlmResponse(llm, msg, docs):
    prompt = PromptTemplate(
        template="""You are an assistant for summarizing text from upcoming events.
        Your task is to use the following documents and describe them to the user in maximum three sentences. 
        Keep it concise.
        If you don't know the answer, just say that you don't know:
        Question: {msg}
        Documents: {docs}
        Answer:
        """,
        input_variables=["msg", "docs"],
        )

    rag_chain = prompt | llm | StrOutputParser()
  
    response = rag_chain.invoke(
        {"msg": msg,
        "docs": docs}
    )
    print(f"{response}")
    return response


def fetchSimilarEvents(msg):
    embedding = model.encode(msg)
    with psycopg2.connect(
        dbname="rag",
        user="postgres",
        password="",
        host="localhost",
        port=5432
    ) as conn:
        register_vector(conn)
        with conn.cursor() as cur:
            # 3. Query for 3 most similar embeddings
            cur.execute("""
            SELECT title, full_desc, place
            FROM events
            ORDER BY embedding <-> %s
            LIMIT %s;
        """, (embedding, 3))
            results = cur.fetchall()
    return results

@app.route('/fetchAll', methods=['GET'])
def fetch_all():
    try:
        message = request.headers.get('Message')
        
        vectorStore = fetchSimilarEvents(message)
        print(message)
        
        
        response = GenerateLlmResponse(llm, message, vectorStore)



        # Return JSON
        return jsonify(response)

    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)



