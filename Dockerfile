FROM python:3.7
ADD . /
WORKDIR /
RUN pip install -r requirements-lock.txt
ENV FLASK_APP=app
ENV FLASK_ENV=production
EXPOSE 5000
ENTRYPOINT flask run
