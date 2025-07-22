# Getting Started with Airflow

This guide explains how to quickly set up and access Apache Airflow in this project.

## 1. Prerequisites
- Docker and Docker Compose installed
- At least 4GB RAM allocated to Docker

## 2. Setup
- Ensure the following directories exist at the project root:
  - `airflow/dags/` (for your DAGs)
  - `airflow/logs/` (for logs)
  - `airflow/plugins/` (for plugins)

## 3. Initialize Airflow
Run this command to set up the Airflow database and create the admin user:

```sh
docker compose up airflow-init
```

## 4. Start Airflow Services
Start all Airflow components:

```sh
docker compose up
```

## 5. Access the Airflow UI
- Open: http://localhost:8080
- Login: `airflow` / `airflow`

## 6. Develop DAGs
- Place your DAG Python files in `airflow/dags/`.

---
For advanced configuration, see the official [Airflow Docker docs](https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html). 
