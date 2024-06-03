FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt requirements.txt

RUN apt-get update && \
    apt-get install -y wget fontconfig && \
    wget https://github.com/iwms/ms-fonts/raw/master/arial.ttf -O /usr/share/fonts/arial.ttf && \
    fc-cache -f -v && \
    pip install --upgrade pip && \
    pip install -r requirements.txt

COPY . /app

EXPOSE 80

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80", "--log-level",  "info"]
