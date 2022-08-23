# syntax=docker/dockerfile:1

FROM python:3.9-bullseye
WORKDIR /app

RUN apt-get update
RUN apt-get install -y locales locales-all
ENV LC_ALL pt_BR.UTF-8
ENV LANG pt_BR.UTF-8
ENV LANGUAGE pt_BR.UTF-8

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip

#Pip command without proxy setting
RUN pip install -r requirements.txt

COPY . .

RUN chmod +x ./entrypoint.sh
ENTRYPOINT ["sh", "entrypoint.sh"]
