Smart Stadium Assistant

A GenAI-powered web application built for PromptWars Virtual — Challenge 4: Smart Stadiums & Tournament Operations, targeting fans, volunteers, and venue staff during live tournament operations at the FIFA World Cup 2026.

Live demo: https://smart-stadium-assistant-rsfr.onrender.com/index.html 
Backend API: hosted on Render: https://smart-stadium-assistant-rsfr.onrender.com 

Architecture


Frontend: Vanilla HTML/CSS/JS, styled with a "schoolbook-meets-stadium" visual identity. Chart.js is loaded via CDN for dashboard visualizations.
Backend: Flask API (app.py), integrating with NVIDIA NIM (Llama 3.1 Nemotron 70B Instruct) for AI inference, with a Gemini fallback and a local mock-response fallback if neither provider is reachable.
Data Layer: Local SQLite database populated with simulated crowd, gate, and incident data. A JSON knowledge base grounds the chatbot's multilingual routing and amenities information.
AI Inference: NVIDIA NIM via an OpenAI-compatible endpoint powers both the fan-facing chatbot and the operations insight generator.


Prerequisites


Python (3.10+)
An NVIDIA NIM API key (build.nvidia.com)


Setup & Local Development

1. Environment Setup

Copy the example environment file and add your NVIDIA_NIM_API_KEY.

cp .env.example .env

2. Generate Seed Data

Generate the local SQLite database (stadium.db) and the knowledge base JSON.

python data/generate_seed.py

3. Start Backend (Flask API)

cd backend
pip install -r requirements.txt
python app.py

The API will run on http://localhost:5000.

4. Start Frontend

Open a new terminal.

cd frontend
python -m http.server 8080

Open http://localhost:8080 in your browser.

Deployment

Frontend is deployed via GitHub Pages, built directly from the main branch root.

Backend is deployed on Render, connected directly to this GitHub repository for automatic redeploys on every push. Environment variables (including NVIDIA_NIM_API_KEY) are configured in the Render dashboard rather than committed to the repo.

The backend was originally deployed on Google Cloud Run. Partway through development, the Google Cloud free trial billing period expired, which disabled that Cloud Run service. The backend was redeployed on Render to keep the live demo link functional. The application code itself is host-agnostic — the Dockerfile and Flask app work unchanged on either platform.


Note: Render's free tier spins down after a period of inactivity. The first request after idle time may take 30-60 seconds to respond while the service wakes up — this is expected, not a bug.



Features


Fan-Facing Chatbot (Multilingual): Ask questions in English, Spanish, or Hindi. The bot detects language automatically and grounds answers in data/knowledge_base.json rather than answering from general model knowledge.
Context-Aware Reasoning: If a fan asks about a gate that isn't wheelchair accessible, the assistant proactively flags this and suggests an accessible alternative, instead of returning only the nearest match.
Operations Dashboard: View simulated crowd density by zone and gate entry flow via Chart.js visualizations.
GenAI Insight: The dashboard runs a deterministic, rule-based threshold check on zone capacity, incident severity, and gate flow, then uses the LLM only to phrase the resulting alert in clear, professional language for staff. Detection logic stays predictable and auditable; GenAI is used only where it adds real value.


Assumptions Made


Crowd, gate, and incident data is simulated, since no live stadium API access was available for this challenge.
Gate accessibility status is illustrative, used to demonstrate the chatbot's context-aware reasoning rather than sourced from an actual venue accessibility audit.
The backend's hosting platform changed mid-development (Cloud Run to Render) due to a GCP trial expiry unrelated to the application code; both are standard container/Flask hosts and the switch required no code changes.
