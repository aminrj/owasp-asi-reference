FROM python:3.11-slim

WORKDIR /opt
COPY _shared/ /opt/_shared/
RUN pip install --no-cache-dir /opt/_shared/agent_harness requests

WORKDIR /app
COPY asi06-memory-poisoning/attack/memory.py /app/memory.py
COPY asi06-memory-poisoning/attack/tools.py /app/tools.py
COPY asi06-memory-poisoning/attack/exploit.py /app/exploit.py

CMD ["python", "exploit.py"]
