FROM python:2
RUN mkdir /meta_rest_api
WORKDIR /meta_rest_api
COPY . /meta_rest_api/
RUN pip install -r requirements.txt
EXPOSE 8081
ENTRYPOINT python manage.py runserver 0.0.0.0:8081