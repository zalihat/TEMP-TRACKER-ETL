# Temp Track ETL

## Overview
Temp Track ETL is a data pipeline that extracts weather data from an external API, processes it using Apache Spark, and loads the transformed data into a PostgreSQL database. The workflow is orchestrated using Apache Airflow, and the infrastructure is managed using Docker.

## Architecture
- **Data Extraction**: Weather data is extracted from an external API and stored in Parquet format.
- **Data Transformation**: Apache Spark processes and cleans the data.
- **Data Loading**: Transformed data is inserted into a PostgreSQL database.
- **Orchestration**: Airflow manages the workflow automation.

## Tech Stack
- **Apache Airflow**: Workflow orchestration (Standalone deployment)
- **Apache Spark**: Data processing
- **PostgreSQL**: Data storage
- **Docker & Docker Compose**: Containerization

## Project Structure
```
├── airflow/
│   ├── dags/
│   │   ├── example_dag
│   │   ├── sample.py
│   │   ├── spark_dag.py
│   │   ├── weather_etl_postgres.py
│   ├── data/
│   ├── logs/
│   │   ├── error.log
│   │   ├── processed_files.log
│   ├── utils/
│   │   ├── utils.py
│   │   ├── transform.py
│   │   ├── run_local.sh
│   ├── .env  # Environment variables file for API key
│   ├── airflow-webserver.pid
│   ├── airflow.cfg
│   ├── standalone_admin_password.txt
│   ├── webserver_config.py
├── docs/
│   ├── architecture.png
├── docker-compose.yml
├── dockerfile
├── dockerfile.spark
├── requirements.txt
```

## Setup & Installation
### Prerequisites
Ensure you have the following installed:
- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/)

### Steps to Run
1. **Clone the Repository:**
   ```sh
   git clone https://github.com/zalihat/TEMP-TRACKER-ETL.git
   cd TEMP-TRACKER-ETL
   ```
2. **Create the `.env` file inside the `airflow/` folder:**
   ```sh
   echo "API_KEY=<your_weatherapi_key>" > airflow/.env
   ```
   Replace `<your_weatherapi_key>` with your actual API key.

3. **Build and Start the Services:**
   ```sh
   docker-compose up --build
   ```
4. **Verify Services:**
   - Airflow UI: [http://localhost:8090](http://localhost:8090)
   - Spark UI: [http://localhost:8080](http://localhost:8080)
   - PostgreSQL: Accessible via `localhost:5432`

## ETL Workflow
1. **Extraction:** Weather data is fetched from the API and stored in `/shared-data/raw/` as Parquet files.
2. **Transformation (Spark):**
   - Column renaming and restructuring.
   - Timestamp conversion.
   - Data validation.
3. **Loading (PostgreSQL):** Processed data is written into a `processed_weather_data` table.

## Running the ETL Pipeline
To trigger the ETL process manually, run:
```sh
docker exec -it airflow airflow dags trigger weather_etl
```
Or wait for Airflow to trigger it as per the DAG schedule.

## Expected Output
The processed data is stored in the PostgreSQL table `processed_weather_data` with the following schema:
| Column Name     | Type       | Description              |
|----------------|-----------|--------------------------|
| location       | TEXT      | Name of the location    |
| region        | TEXT      | Region of the location  |
| country       | TEXT      | Country of the location |
| lat           | FLOAT     | Latitude                |
| lon           | FLOAT     | Longitude               |
| localtime     | TIMESTAMP | Local time of record    |
| temperature_c | FLOAT     | Temperature (Celsius)   |
| temperature_f | FLOAT     | Temperature (Fahrenheit) |
| feelslike_c   | FLOAT     | Feels-like temp (C)     |
| feelslike_f   | FLOAT     | Feels-like temp (F)     |
| date          | DATE      | Recorded date           |

## Logs & Debugging
- **Airflow logs**: `./airflow/logs/`
- **Spark logs**: `./error.log`
- **PostgreSQL logs**: Check container logs using:
  ```sh
  docker logs postgres
  ```



