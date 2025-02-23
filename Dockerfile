# Use official Airflow image
FROM apache/airflow:2.10.5-python3.12

# Set environment variables for Airflow
ENV AIRFLOW_HOME=/opt/airflow
ENV AIRFLOW_UID=50000
ENV AIRFLOW_GID=50000

# Install necessary Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your DAGs and scripts into the container
COPY dags/ $AIRFLOW_HOME/dags/
COPY scripts/ $AIRFLOW_HOME/scripts/
ENV GOOGLE_APPLICATION_CREDENTIALS scripts/service_account.json

# Give airflow user access to the dags and scripts
USER root
RUN chown -R ${AIRFLOW_UID}:${AIRFLOW_GID} $AIRFLOW_HOME

# Update package list and install dependencies
RUN apt-get update && apt-get install -y \
    wget curl gnupg2 lsb-release ca-certificates openjdk-17-jdk && apt-get clean

# Set the Java version you want to install (Oracle or OpenJDK)
ENV JAVA_VERSION=17
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk
ENV PATH="${JAVA_HOME}/bin:${PATH}"

# Download and install OpenJDK 17 (or you can use a direct link to any version)
RUN wget --no-verbose https://download.oracle.com/java/17/archive/jdk-17.0.12_linux-aarch64_bin.tar.gz \
    && tar -xzf jdk-17.0.12_linux-aarch64_bin.tar.gz \
    && mv jdk-17.0.12 /usr/lib/jvm/java-17-openjdk \
    && rm jdk-17.0.12_linux-aarch64_bin.tar.gz

# Download jars
# Download the GCS connector JAR (for GCS integration with Spark)
RUN wget -P $AIRFLOW_HOME/jars/ https://github.com/GoogleCloudDataproc/hadoop-connectors/releases/download/v3.0.4/gcs-connector-3.0.4-shaded.jar

# Download the Spark BigQuery connector JAR
RUN wget -P $AIRFLOW_HOME/jars/ https://storage.googleapis.com/spark-lib/bigquery/spark-3.5-bigquery-0.42.0.jar

# Switch back to airflow user
USER ${AIRFLOW_UID}

# Start Airflow services (webserver, scheduler, etc.)
ENTRYPOINT ["/entrypoint"]
CMD ["webserver"]