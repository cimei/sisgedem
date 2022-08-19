# syntax=docker/dockerfile:1

FROM python:3.9-bullseye
WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip

#Pip command without proxy setting
RUN pip install -r requirements.txt

COPY . .

RUN chmod +x ./entrypoint.sh
ENTRYPOINT ["sh", "entrypoint.sh"]
