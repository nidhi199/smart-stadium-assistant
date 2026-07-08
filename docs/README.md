# Smart Stadium Assistant

A GenAI-powered web application for the FIFA World Cup 2026, targeting fans, volunteers, and venue staff during live tournament operations.

## Architecture
- **Frontend**: Vanilla HTML/JS with Vite, styling inspired by a premium "schoolbook-meets-stadium" visual identity.
- **Backend**: Flask API (`app.py`), integrating with Google Gemini AI.
- **Data Layer**: Local SQLite database populated with simulated crowd, gate, and incident data. A JSON knowledge base powers the LLM's multilingual routing and amenities information.
- **AI Inference**: Uses Google Gemini via Vertex AI / GenAI SDK to power the fan-facing chatbot and operation insight generator.

## Prerequisites
- Node.js (v16+)
- Python (3.10+)
- Google Gemini API Key

## Setup & Local Development

### 1. Environment Setup
Copy the example environment file and add your `GEMINI_API_KEY`.
```bash
cp .env.example .env
```

### 2. Generate Seed Data
Generate the local SQLite database (`stadium.db`) and the knowledge base JSON.
```bash
python data/generate_seed.py
```

### 3. Start Backend (Flask API)
```bash
cd backend
pip install -r requirements.txt
python app.py
```
The API will run on `http://localhost:5000`.

### 4. Start Frontend (Vite)
Open a new terminal.
```bash
cd frontend
npm install
npm run dev
```
Open the provided Vite localhost URL in your browser.

## Cloud Run Deployment

To deploy the backend to Google Cloud Run, build the Docker image from the **root** of the repository:

```bash
# Build the image
docker build -t smart-stadium-backend -f backend/Dockerfile .

# Push to Artifact Registry (replace with your project details)
docker tag smart-stadium-backend gcr.io/YOUR_PROJECT_ID/smart-stadium-backend
docker push gcr.io/YOUR_PROJECT_ID/smart-stadium-backend

# Deploy to Cloud Run
gcloud run deploy smart-stadium-api \
  --image gcr.io/YOUR_PROJECT_ID/smart-stadium-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GEMINI_API_KEY="your_actual_api_key_here"
```

## Features

- **Fan-Facing Chatbot (Multilingual):** Ask questions in English, Spanish, or Hindi. The bot detects language automatically and grounds answers based on `data/knowledge_base.json`.
- **Operations Dashboard:** View real-time (simulated) crowd density by zone and gate entry flow via Chart.js visualizations.
- **GenAI Insight:** The dashboard automatically checks rule-based thresholds and triggers a Gemini inference call to summarize active alerts into plain, actionable language.
