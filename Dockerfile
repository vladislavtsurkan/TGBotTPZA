FROM python:3.11.0

WORKDIR /bot

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .