FROM python:3.8
RUN mkdir /app
WORKDIR /app
COPY ./libs.txt /app/libs.txt
RUN apt update
RUN pip install -r libs.txt