# Travel Recommendation System

[![CI](https://github.com/ykykyk0814/TRS/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/ykykyk0814/TRS/actions/workflows/ci.yml)

This project aims to provide travellers personalized travel plans with FastAPI Users authentication system.

## 🚀 Quick Start

### Option 1: Main Application Only
```sh
# 1. Copy environment template
cp env.template .env

# 2. Start databases (PostgreSQL + Qdrant)
./docker-manage.sh up main

# 3. Install dependencies and run migrations
pip install -r requirements.txt
alembic upgrade head

# 4. Start API server
uvicorn app.main:app --reload
```

### Option 2: Full Stack with Airflow
```sh
# 1. Copy environment template
cp env.template .env

# 2. Initialize Airflow (first time only)
./docker-manage.sh init

# 3. Start all services (app + Airflow)
./docker-manage.sh up

# 4. Install dependencies and run migrations
pip install -r requirements.txt
alembic upgrade head

# 5. Start API server
uvicorn app.main:app --reload
```

## 🔗 Access Points

- **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Airflow UI**: [http://localhost:8080](http://localhost:8080) (username: `airflow` password:`airflow`)
- **PostgreSQL**: `localhost:5432` (user: `postgres`/`postgres`)
- **Qdrant**: `localhost:6333`

## 🎛️ Docker Management

```sh
# Start/stop services
./docker-manage.sh up [main|airflow|all]     # Start services
./docker-manage.sh down [main|airflow|all]   # Stop services
./docker-manage.sh status                    # Check status
./docker-manage.sh logs [main|airflow|all]   # View logs

# Examples
./docker-manage.sh up main      # Start only databases
./docker-manage.sh logs airflow # View Airflow logs
```

> 📚 **Detailed setup guide**: See [DOCKER_SETUP.md](DOCKER_SETUP.md)

## API Verification

- Use `tests/verify_endpoints.py` to quickly verify all major API endpoints and authentication.
- It tests:
  - Health endpoints (`/health`, `/info`)
  - User registration and JWT authentication
  - Current user profile (`/auth/users/me`)
  - Preferences CRUD
  - Tickets CRUD
- Run it manually:
  ```sh
  python tests/verify_endpoints.py
  ```
- Note: This script is not picked up by pytest and is for manual/CI verification.

## Contributing

- **Code style:** Use `black` for formatting and `flake8` for linting
- **Testing:** Write tests for new features
- **Database:** Use Alembic for database migrations
