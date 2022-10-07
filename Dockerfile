# syntax=docker/dockerfile:1

FROM python:3.9-bullseye
WORKDIR /app

ENV PYTHONIOENCODING=utf-8

ENV TZ="America/Sao_Paulo"

ENV PYTHONUNBUFFERED=1

RUN apt-get update

# estabelece padrão brasileiro no locale
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
