
FROM python:3.9-slim

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

# Usually its port 80 for web services
# But Koyeb uses port 8000 as default for web services
EXPOSE 8000

CMD ["python", "main.py"]
