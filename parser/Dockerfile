#Dockerfile parser
FROM python:3.11-slim

WORKDIR /parser

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . .

CMD ["python", "main.py"]