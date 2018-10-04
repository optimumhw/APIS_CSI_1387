#FROM python:3.5.2-slim
#RUN mkdir -p /usr/src/app
#WORKDIR /usr/src/app
#COPY requirements.txt /usr/src/app
#RUN apt-get update && \
#apt-get install -y python-psycopg2 libpq-dev cython && \
#pip install --upgrade pip && pip install -r requirements.txt
#COPY . /usr/src/app
#EXPOSE 5002
#CMD ["python", "./tsapi.py"]

FROM python:3.6
COPY . /app
WORKDIR /app
RUN pip install --upgrade pip && pip install -r requirements.txt
EXPOSE $PORT
CMD python ./tsapi.py