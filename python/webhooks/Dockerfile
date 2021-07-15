FROM python:3.7-alpine

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

RUN mkdir /app
WORKDIR /app
COPY webhook.py /app

RUN adduser -D user
USER user

EXPOSE 9998

CMD ["python", "webhook.py", "9998"]