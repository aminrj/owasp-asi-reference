# Build context is the REPO ROOT (see docker-compose.yml: context: ../..),
# so that both shared/ and this category's files are visible to COPY.
FROM python:3.12-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1
COPY ASI06_memory_poisoning/attack/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY shared/ ./shared/
COPY ASI06_memory_poisoning/attack/ ./
