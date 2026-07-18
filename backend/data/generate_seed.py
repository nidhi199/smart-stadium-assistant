import sqlite3
import json
import os
import random
from datetime import datetime, timedelta

def generate_sqlite_db():
    db_path = os.path.join(os.path.dirname(__file__), 'stadium.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='zones'")
    table_exists = cursor.fetchone()
    if table_exists:
        cursor.execute("SELECT COUNT(*) FROM zones")
        if cursor.fetchone()[0] > 0:
            print("Database already seeded, skipping.")
            conn.close()
            return

    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS zones (
            id INTEGER PRIMARY KEY,
            zone_name TEXT,
            current_capacity INTEGER,
            max_capacity INTEGER
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS incidents (
            id INTEGER PRIMARY KEY,
            description TEXT,
            severity TEXT,
            zone_name TEXT,
            timestamp TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS gate_flow (
            id INTEGER PRIMARY KEY,
            gate_name TEXT,
            entry_rate_per_min INTEGER
        )
    ''')

    # Clear old data
    cursor.execute('DELETE FROM zones')
    cursor.execute('DELETE FROM incidents')
    cursor.execute('DELETE FROM gate_flow')

    # Insert Zones
    zones = [
        ("North Concourse", 4500, 5000),
        ("South Concourse", 3200, 5000),
        ("East Wing", 4800, 5000),  # High capacity - potential alert
        ("West Wing", 2100, 5000),
        ("VIP Lounge", 150, 300)
    ]
    cursor.executemany('INSERT INTO zones (zone_name, current_capacity, max_capacity) VALUES (?, ?, ?)', zones)

    # Insert Incidents
    now = datetime.now()
    incidents = [
        ("Spilled drink causing slip hazard", "Low", "South Concourse", (now - timedelta(minutes=15)).isoformat()),
        ("Escalator E2 malfunction", "Medium", "East Wing", (now - timedelta(minutes=5)).isoformat()),
        ("Crowd bottleneck near Gate C", "High", "North Concourse", now.isoformat())
    ]
    cursor.executemany('INSERT INTO incidents (description, severity, zone_name, timestamp) VALUES (?, ?, ?, ?)', incidents)

    # Insert Gate Flow
    gates = [
        ("Gate A", 45),
        ("Gate B", 120), # High entry rate
        ("Gate C", 85),
        ("Gate D", 30)
    ]
    cursor.executemany('INSERT INTO gate_flow (gate_name, entry_rate_per_min) VALUES (?, ?)', gates)

    conn.commit()
    conn.close()
    print(f"Database generated at {db_path}")

def generate_knowledge_base():
    kb_path = os.path.join(os.path.dirname(__file__), 'knowledge_base.json')
    
    # Multilingual knowledge base
    kb = {
        "gates": [
            {
                "id": "gate_a",
                "name": "Gate A",
                "nearest_sections": ["101", "102", "103"],
                "accessible": True,
                "info": {
                    "en": "Gate A is located on the North side. It is fully accessible.",
                    "es": "La Puerta A está ubicada en el lado norte. Es totalmente accesible.",
                    "hi": "गेट A उत्तर दिशा में स्थित है। यह पूरी तरह से सुलभ है।"
                }
            },
            {
                "id": "gate_c",
                "name": "Gate C",
                "nearest_sections": ["110", "111", "112"],
                "accessible": False,
                "info": {
                    "en": "Gate C is on the East side. For accessible entry, please use Gate A or D.",
                    "es": "La Puerta C está en el lado este. Para entrada accesible, use la Puerta A o D.",
                    "hi": "गेट C पूर्व दिशा में है। सुलभ प्रवेश के लिए कृपया गेट A या D का उपयोग करें।"
                }
            }
        ],
        "transport": [
            {
                "type": "metro",
                "name": "Stadium Central Metro",
                "info": {
                    "en": "The Metro runs every 5 minutes after the match. Exit via the South Concourse for the fastest route.",
                    "es": "El metro pasa cada 5 minutos después del partido. Salga por el South Concourse para la ruta más rápida.",
                    "hi": "मैच के बाद मेट्रो हर 5 मिनट में चलती है। सबसे तेज़ रास्ते के लिए साउथ कॉनकोर्स से बाहर निकलें।"
                }
            }
        ],
        "amenities": [
            {
                "type": "restroom",
                "accessible": True,
                "info": {
                    "en": "Accessible restrooms are located near Sections 105, 112, and 120.",
                    "es": "Los baños accesibles se encuentran cerca de las secciones 105, 112 y 120.",
                    "hi": "सुलभ शौचालय सेक्शन 105, 112 और 120 के पास स्थित हैं।"
                }
            }
        ]
    }
    
    with open(kb_path, 'w', encoding='utf-8') as f:
        json.dump(kb, f, indent=2, ensure_ascii=False)
    
    print(f"Knowledge base generated at {kb_path}")

if __name__ == "__main__":
    generate_sqlite_db()
    generate_knowledge_base()
    print("Seed data generation complete.")
