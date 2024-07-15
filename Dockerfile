
FROM python:3.9-slim

WORKDIR /app
COPY . /app

RUN apt-get update && apt-get install -y ffmpeg
RUN pip install --no-cache-dir -r requirements.txt

# Let Flask app listen on port 8000
EXPOSE 8000

CMD ["python", "main.py"]
