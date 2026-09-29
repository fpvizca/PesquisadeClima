FROM python:3.12-slim

WORKDIR /app

# matplotlib e python-docx dependem de binarios de sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libffi-dev fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

#COPY . .

ENV PORT=8120 \
    PYTHONUNBUFFERED=1 \
    FLASK_DEBUG=false

EXPOSE 8120

# Aplica migracoes antes de subir o servidor
CMD ["sh", "-c", "python migrar.py && gunicorn --bind 0.0.0.0:${PORT} --workers 4 --timeout 180 --access-logfile - --error-logfile - app:app"]
