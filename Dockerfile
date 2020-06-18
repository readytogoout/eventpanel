FROM python:3.7
ADD . /
WORKDIR /
RUN pip install -r requirements-lock.txt
ENV FLASK_APP=app
ENV FLASK_ENV=production
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000
EXPOSE 5000
ENTRYPOINT flask run
