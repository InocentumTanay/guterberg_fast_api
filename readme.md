# FastAPI Project with PostgreSQL (Docker)

This guide will walk you through setting up a FastAPI project with PostgreSQL using Docker. It covers database restoration, model generation, schema creation, and API documentation.

---

## 1. Setup Docker and Project

### **Prerequisites:**
- Install **Docker** and **Docker Compose**
- Install **Python 3.9+** and **pip**

### **Clone the repository**
```sh
git clone <your-repo-url>
cd <your-project-folder>
```

### **Create a `docker-compose.yml` file**
```yaml
version: '3.8'

services:
  db:
    image: postgres:13
    restart: always
    environment:
      POSTGRES_USER: YOUR_USER
      POSTGRES_PASSWORD: YOUR_PASSWORD
      POSTGRES_DB: DB_NAME
    ports:
      - "5432:5432"
    volumes:
      - pg_data:/var/lib/postgresql/data

  app:
    build: .
    container_name: fastapi_app
    depends_on:
      - db
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: "postgresql://YOUR_USER:YOUR_PASSWORD@db/DB_NAME"
    volumes:
      - .:/app
    command: ["uvicorn", "main:app", "--host", "0.0.0.0", "--reload"]

volumes:
  pg_data:
```

### **Run Docker Containers**
```sh
docker-compose up --build -d
```

---

## 2. Restore Database from Dump
If you have a PostgreSQL dump file, restore it with:
```sh
docker cp dump.sql <container_id>:/dump.sql
docker exec -it <container_id> psql -U YOUR_USER -d DB_NAME -f /gutendex.dump
```
Alternatively, using a local `psql` client:
```sh
PGPASSWORD=YOUR_PASSWORD psql -h localhost -U YOUR_USER -d DB_NAME -f gutendex.dump
```

---

## 3. Copy Database Models from Existing DB to FastAPI
Use **sqlacodegen** to generate SQLAlchemy models:
```sh
pip install sqlacodegen
sqlacodegen postgresql://YOUR_USER:YOUR_PASSWORD@db/DB_NAME --outfile models.py
```

Place `models.py` inside your FastAPI project.

---

## 4. Run FastAPI Project
Ensure dependencies are installed:
```sh
pip install -r requirements.txt
```
Run the app:
```sh
uvicorn main:app --reload
```
The API will be available at: [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## 5. Create Pydantic Schemas
Create a `schemas.py` file to define data validation models:

```python
from pydantic import BaseModel
from typing import List, Optional

class BooksBookSchema(BaseModel):
    id: int
    gutenberg_id: int
    title: str
    media_type: str
    download_count: int
    
    class Config:
        orm_mode = True
```

Use it in your FastAPI routes:
```python
@app.get("/books/", response_model=List[BooksBookSchema])
def get_books(db: Session = Depends(get_db)):
    return db.query(BooksBook).all()
```

---

## 6. Generate API Documentation
FastAPI automatically provides **Swagger UI** and **Redoc**.

- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Redoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 🎉 Done! Your FastAPI project is now fully set up with PostgreSQL and auto-generated API docs.