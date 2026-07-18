from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import sqlite3
import json
import os
from llm import chat_with_fan, generate_insight

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": ["https://nidhi199.github.io", "http://localhost:8080", "http://127.0.0.1:8080"]}})

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

REQUIRED_ENV_VARS = ["NVIDIA_NIM_API_KEY"]
missing_vars = [var for var in REQUIRED_ENV_VARS if not os.environ.get(var)]
if missing_vars:
    print(f"WARNING: Missing required environment variables: {missing_vars}. The app will run but AI features will fail.")

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
@limiter.limit("10 per minute")
def chat():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid or missing JSON body"}), 400

    user_message = data.get('message', '')

    if not isinstance(user_message, str) or not user_message.strip():
        return jsonify({"error": "Message is required"}), 400

    if len(user_message) > 500:
        return jsonify({"error": "Message too long (max 500 characters)"}), 400

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
    debug_mode = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
