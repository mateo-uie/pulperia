FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p data

EXPOSE 80

# Evita el buffering de salida
ENV PYTHONUNBUFFERED=1 

CMD ["python3", "main.py"]
