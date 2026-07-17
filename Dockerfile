# Build context should be the root repository directory (e.g., `docker build -t smart-stadium-backend -f backend/Dockerfile .`)
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy the data directory so the backend can access the SQLite DB and KB
COPY data/ ./data/

# Copy backend requirements and install
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r ./backend/requirements.txt

# Copy backend source code
COPY backend/ ./backend/

# Set working directory to backend for execution
WORKDIR /app/backend

# Expose port (Cloud Run uses PORT env var, default to 8080)
ENV PORT=8080
EXPOSE 8080

# Command to run the application using Gunicorn for production
# Fallback to python app.py if gunicorn isn't installed
CMD ["sh", "-c", "python ../data/generate_seed.py && python app.py"]
