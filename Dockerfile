FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

WORKDIR /src

COPY . /src

RUN pip install -r requirements.txt

RUN apt-get update && \
    apt-get install -y postgresql-client && \
    rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y locales locales-all && rm -rf /var/lib/apt/lists/*

# Генерируем и устанавливаем локаль
RUN echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && locale-gen en_US.UTF-8

# Локаль по умолчанию
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8