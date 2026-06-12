# Build context is the REPO ROOT (see docker-compose.yml: context: ../..),
# so that both shared/ and this category's files are visible to COPY.
# NB: the ASI01/02/06 Dockerfiles use a different (broken) context — see
# the repo review notes. This is the corrected pattern.
FROM python:3.12-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1
COPY ASI04_supply_chain/attack/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY shared/ ./shared/
COPY ASI04_supply_chain/attack/ ./
