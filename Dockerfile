FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Fixed: points to api.main instead of just main
CMD uvicorn api.main:app --host 0.0.0.0 --port $PORT