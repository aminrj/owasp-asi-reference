# Build context is the repo root so we can COPY _shared/.
FROM python:3.11-slim

WORKDIR /opt
COPY _shared/ /opt/_shared/
RUN pip install --no-cache-dir /opt/_shared/agent_harness requests

WORKDIR /app
COPY asi02-tool-misuse/attack/tools.py /app/tools.py
COPY asi02-tool-misuse/attack/exploit.py /app/exploit.py

# Plant the "secret" the attack will steal.
RUN mkdir -p /etc/agent_secrets \
 && echo -n "sk-supersecret-do-not-leak" > /etc/agent_secrets/api_key.txt

CMD ["python", "exploit.py"]
