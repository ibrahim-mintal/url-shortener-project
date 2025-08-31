FROM python:3.11-slim

WORKDIR /app

RUN apt-get update

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD ["python3", "app.py"]


