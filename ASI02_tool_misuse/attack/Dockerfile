# Build context is the REPO ROOT (see docker-compose.yml: context: ../..),
# so that both shared/ and this category's files are visible to COPY.
FROM python:3.12-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1
COPY ASI02_tool_misuse/attack/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY shared/ ./shared/
COPY ASI02_tool_misuse/attack/ ./
