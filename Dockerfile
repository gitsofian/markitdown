FROM python:3.12-slim

WORKDIR /app

# Installe les dépendances système
RUN apt-get update && apt-get install -y \
    libmagic1 ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Installe les dépendances Python
COPY api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie le code API
COPY api/ .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]