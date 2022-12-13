FROM python:3.11.1

RUN pip install --upgrade pip

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY ./src ./src

WORKDIR /src
