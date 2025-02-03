FROM apache/airflow:latest
USER root
RUN apt-get update && \
    apt-get -y install git && \
    apt-get install -y openjdk-17-jre wget tar && \
    apt-get clean
# Set JAVA_HOME environment variable
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
USER airflow
COPY requirements.txt  tmp/requirements.txt
# Copy your Spark application (app.py) into the Airflow container
COPY app.py /opt/spark/app.py
RUN pip install --no-cache-dir -r tmp/requirements.txt
