from flask import Flask, jsonify, request
import psycopg2
from flask_cors import CORS

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser



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

@app.route('/fetchAll', methods=['GET'])
def fetch_all():
    try:
        message = request.headers.get('Message')
        
        # Connect to PostgreSQL
        """ 
conn = psycopg2.connect(
            database="rag",
            user="postgres",
            password="",
        )
        cur = conn.cursor()

        # # Execute query
        cur.execute('SELECT * FROM events')

        # # Fetch all rows
        rows = cur.fetchall()

        # # Optional: get column names
        colnames = [desc[0] for desc in cur.description]

        # # Convert each row to a dict
        results = [dict(zip(colnames, row)) for row in rows]

        # # Cleanup
        cur.close()
        conn.close()
        """
        print(message)
        
        vectorStore = "Guidad visning \n\nAtt följa med på en inspirerande visning är en bra ingång till konsten. Välkommen på egen hand eller stäm träff med en vän. Fri entré."
        
        response = GenerateLlmResponse(llm, message, vectorStore)



        # Return JSON
        return jsonify(response)

    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)



