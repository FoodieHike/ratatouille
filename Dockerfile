FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY ./app /app


RUN apt-get update && \
    apt-get install -y postgresql-client && \
    rm -rf /var/lib/apt/lists/*

COPY db_wait.sh /

COPY start.sh /

RUN chmod +x /start.sh

RUN chmod +x /db_wait.sh