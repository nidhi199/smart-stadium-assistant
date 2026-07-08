from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import json
import os
from llm import chat_with_fan, generate_insight

app = Flask(__name__)
# Enable CORS for all routes and origins (for dev)
CORS(app, resources={r"/api/*": {"origins": "*"}})

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'stadium.db')
KB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'knowledge_base.json')

def load_knowledge_base():
    try:
        with open(KB_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading KB: {e}")
        return {}

def get_stadium_data():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    data = {}
    
    cursor.execute("SELECT * FROM zones")
    data['zones'] = [dict(row) for row in cursor.fetchall()]
    
    cursor.execute("SELECT * FROM incidents")
    data['incidents'] = [dict(row) for row in cursor.fetchall()]
    
    cursor.execute("SELECT * FROM gate_flow")
    data['gate_flow'] = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return data

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    
    if not user_message:
        return jsonify({"error": "Message is required"}), 400
        
    kb = load_knowledge_base()
    kb_context = json.dumps(kb, ensure_ascii=False)
    
    response = chat_with_fan(user_message, kb_context)
    return jsonify({"reply": response})

@app.route('/api/dashboard', methods=['GET'])
def dashboard_data():
    data = get_stadium_data()
    return jsonify(data)

@app.route('/api/insight', methods=['GET'])
def insight():
    data = get_stadium_data()
    insight_text = generate_insight(data)
    return jsonify({"insight": insight_text})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
