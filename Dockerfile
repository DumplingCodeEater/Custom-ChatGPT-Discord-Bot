
FROM python:3.9-slim

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

# Flask app is listening on port 8080
EXPOSE 8080

CMD ["python", "main.py"]
