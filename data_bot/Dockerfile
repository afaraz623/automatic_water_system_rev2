# first stage
FROM python:3.10-slim AS builder

WORKDIR /data_bot

COPY requirements.txt .

RUN pip3 install --no-cache-dir -r requirements.txt

# second stage
FROM python:3.10-slim

WORKDIR /data_bot

COPY --from=builder /usr/local/lib/python3.10/site-packages/ /usr/local/lib/python3.10/site-packages/
COPY main.py .
COPY logs.py .

CMD ["python3", "main.py"]