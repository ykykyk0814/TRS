# Travel Recommendation System

[![CI](https://github.com/ykykyk0814/TRS/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/ykykyk0814/TRS/actions/workflows/ci.yml)

This project aims to provide travellers personalized travel plans with FastAPI Users authentication system.

## 🚀 Quick Start

### Option 1: Main Application Only
```sh
# 1. Copy environment template
cp env.template .env

# 2. Configure environment variables
# Edit .env file and add:
# - Amadeus API credentials (required for Airflow DAGs)
# - AIRFLOW_UID (to avoid permission issues if using Airflow later)
# AMADEUS_CLIENT_ID=your_amadeus_client_id_here
# AMADEUS_CLIENT_SECRET=your_amadeus_client_secret_here
# AIRFLOW_UID=501  # Replace with your user ID (run 'id -u' to get it)
# Get Amadeus credentials from: https://developers.amadeus.com/

# 3. Start databases (PostgreSQL + Qdrant)
./docker-manage.sh up main

# 4. Install dependencies and run migrations
pip install -r requirements.txt
alembic upgrade head

# 5. Start API server
uvicorn app.main:app --reload
```

### Option 2: Full Stack with Airflow
```sh
# 1. Copy environment template
cp env.template .env

# 2. Configure environment variables
# Edit .env file and add:
# - Amadeus API credentials (required for Airflow DAGs)
# - AIRFLOW_UID (to avoid permission issues)
# AMADEUS_CLIENT_ID=your_amadeus_client_id_here
# AMADEUS_CLIENT_SECRET=your_amadeus_client_secret_here
# AIRFLOW_UID=501  # Replace with your user ID (run 'id -u' to get it)
# Get Amadeus credentials from: https://developers.amadeus.com/

# 3. Initialize Airflow (first time only)
./docker-manage.sh init

# 4. Start all services (app + Airflow)
./docker-manage.sh up

# 5. Install dependencies and run migrations
pip install -r requirements.txt
alembic upgrade head

# 6. Start API server
uvicorn app.main:app --reload
```

## 🔗 Access Points

- **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Airflow UI**: [http://localhost:8080](http://localhost:8080) (username: `airflow` password:`airflow`)
- **PostgreSQL**: `localhost:5432` (user: `postgres`/`postgres`)
- **Qdrant**: `localhost:6333`

## 🧠 Vector Database Setup

### Quick Setup
```bash
# 1. Start services
./docker-manage.sh up main

# 2. Install dependencies
pip install -r requirements.txt

# 3. Setup Qdrant with test data
python scripts/setup_qdrant.py
```

### Vector API Endpoints
- `POST /api/vector/collections` - Create collection
- `GET /api/vector/collections/{name}` - Get collection info
- `POST /api/vector/content` - Add travel content
- `POST /api/vector/search` - Search travel content
- `POST /api/vector/test-data` - Add test data
- `GET /api/vector/health` - Health check

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

## 🔧 Troubleshooting

### Airflow Permission Issues
If you encounter permission errors with Airflow (like "Could not read served logs: 404 Client Error"), it's likely due to user ID mismatch between your host system and Docker containers.

**Solution:**
1. Check your user ID: `id -u`
2. Set the `AIRFLOW_UID` in your `.env` file to match your user ID:
   ```bash
   # Add this to your .env file
   AIRFLOW_UID=501  # Replace 501 with your actual user ID
   ```
3. Restart Airflow services:
   ```bash
   ./docker-manage.sh down airflow
   ./docker-manage.sh up airflow
   ```

**Why this happens:** Docker containers run as a different user ID than your host system, causing permission issues with mounted volumes. Setting `AIRFLOW_UID` ensures the containers run as your user ID.

### Common Issues
- **Database connection errors:** Ensure PostgreSQL is running with `./docker-manage.sh status`
- **Airflow DAG import errors:** Check that all required environment variables are set in `.env`
- **Permission denied errors:** See Airflow Permission Issues above

## Contributing

- **Code style:** Use `black` for formatting and `flake8` for linting
- **Testing:** Write tests for new features
- **Database:** Use Alembic for database migrations
