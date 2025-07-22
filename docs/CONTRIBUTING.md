# Adding a New Data Table & Repository

## 1. Add a New Data Table (Model)
- Define your model in `app/core/models.py`.
- Inherit from `Base` and set `__tablename__`.
- Use SQLAlchemy columns and relationships as needed.

Example:
```python
class MyTable(Base):
    __tablename__ = "my_table"
    id: Mapped[int] = mapped_column(primary_key=True)
    # Add your fields here
```

## 2. Create a Repository
- Create a new file in `app/repository/`, e.g., `my_table.py`.
- Inherit from `BaseRepository` and specify your model and schemas.

Example:
```python
from app.repository.base import BaseRepository
from app.core.models import MyTable

class MyTableRepository(BaseRepository[MyTable, CreateSchema, UpdateSchema]):
    def __init__(self):
        super().__init__(MyTable)
```

## 3. (Optional) Add Service, API, and Schemas
- Follow the existing patterns in `app/service/`, `app/api/`, and `app/dto/` for business logic, endpoints, and Pydantic schemas.

## 4. Run Migrations
- After editing models, generate and apply a migration:
  ```sh
  alembic revision --autogenerate -m "add my_table"
  alembic upgrade head
  ``` 