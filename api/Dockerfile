FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
COPY requirements-test.txt .

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r requirements-test.txt

# Ajout de l'environnement Python
ENV PYTHONPATH=/app

COPY . .

RUN mkdir -p /usr/share/fonts

COPY /fonts /usr/share/fonts

EXPOSE 80

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]