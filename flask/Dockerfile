FROM python:3.8
RUN mkdir /app
WORKDIR /app
ADD . /app
RUN apt update
RUN pip install -r libs.txt
CMD ["uwsgi", "app.ini"]