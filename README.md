# Travel Recommendation System

This project aims to provide travellers personalized travel plans with FastAPI Users authentication system.

## Quickstart

1. **Copy environment template and edit as needed:**
   ```sh
   cp env.template .env
   ```

2. **Start dependencies (Postgres, Qdrant) with Docker Compose:**
   ```sh
   docker-compose up -d
   ```

3. **Install Python dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

4. **Run database migrations:**
   ```sh
   alembic upgrade head
   ```

5. **Start the API server:**
   ```sh
   uvicorn app.main:app --reload
   ```

6. **Access API docs:**
   - Open [http://localhost:8000/docs](http://localhost:8000/docs) in your browser.

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

- **Code style:** Use `