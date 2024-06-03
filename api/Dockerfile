FROM python:3.10-slim-bullseye

WORKDIR /app

COPY requirements.txt requirements.txt

RUN apt-get update && \
    pip install --upgrade pip && \
    pip install -r requirements.txt

COPY . /app

RUN mkdir -p /usr/share/fonts

COPY /fonts /usr/share/fonts

EXPOSE 80

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80", "--log-level", "info"]
