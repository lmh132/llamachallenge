FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install PostgreSQL client
RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*

# Copy source code
COPY . .

# Wait for DB and run migrations
CMD ["bash", "-c", "python init_db.py && alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8000"]