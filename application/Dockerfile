FROM python:3.8-alpine

COPY ./app /app

WORKDIR /app

RUN pip install -r requirements.txt

CMD [ "python", "app.py" ]