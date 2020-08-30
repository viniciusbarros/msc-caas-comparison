FROM tiangolo/uwsgi-nginx-flask:python3.8-alpine

COPY ./requirements.txt /var/www/requirements.txt
RUN pip install -r /var/www/requirements.txt

COPY ./app /app


