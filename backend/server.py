from flask import Flask, jsonify, request
import psycopg2
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

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



        # Return JSON
        return jsonify("Guidad visning \n\nAtt följa med på en inspirerande visning är en bra ingång till konsten. Välkommen på egen hand eller stäm träff med en vän. Fri entré.")

    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
