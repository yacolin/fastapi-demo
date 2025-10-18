# FastAPI Demo - Media Management API

A modern, asynchronous RESTful API built with FastAPI for managing albums, songs, and media items. Features standardized response handling, comprehensive error management, and async database operations.

## 🚀 Features

- **Modern Async Architecture**: Built on FastAPI with full async/await support
- **RESTful API Design**: Clean, versioned API endpoints (`/api/v1/`)
- **Standardized Responses**: Unified response format with business codes
- **Comprehensive Error Handling**: Centralized exception handlers with detailed logging
- **Database Operations**: SQLAlchemy 2.0+ with async MySQL/SQLite support
- **Type Safety**: Full Pydantic v2 validation and type hints
- **Pagination Support**: List endpoints with total count metadata
- **Task Queue Ready**: Celery integration for background jobs
- **Security Features**: JWT, bcrypt, and cryptography support

## 📋 Tech Stack

### Core Framework

- **FastAPI** (v0.119.0) - Modern web framework
- **Uvicorn** (v0.37.0) - ASGI server
- **Pydantic** (v2.11.7) - Data validation

### Database

- **SQLAlchemy** (v2.0.44) - ORM with async support
- **aiomysql** (v0.2.0) - Async MySQL driver
- **aiosqlite** (v0.21.0) - Async SQLite driver

### Background Tasks

- **Celery** (v5.5.3) - Distributed task queue
- **Redis** (v6.4.0) - Message broker

### Security

- **PyJWT** (v2.10.1) - JSON Web Tokens
- **bcrypt** (v5.0.0) - Password hashing
- **cryptography** (v46.0.3) - Cryptographic operations

### Monitoring & Logging

- **Loguru** (v0.7.3) - Advanced logging
- **Sentry SDK** (v2.42.0) - Error tracking

## 📁 Project Structure

```
fastapi-demo/
├── configs/              # Configuration modules
│   ├── __init__.py      # Config exports
│   └── db.py            # Database configuration
├── controllers/         # API route handlers
│   ├── __init__.py      # Router aggregation with /api/v1/ prefix
│   ├── album.py         # Album CRUD endpoints
│   ├── song.py          # Song CRUD endpoints
│   ├── item.py          # Item CRUD endpoints
│   └── team.py          # Team CRUD endpoints
├── utils/               # Shared utilities
│   ├── __init__.py      # Utils exports
│   ├── biz_code.py      # Business status codes
│   ├── restful.py       # RESTful response utilities
│   ├── exception_handlers.py  # Global exception handlers
│   └── USAGE_EXAMPLES.md      # Utility usage guide
├── main.py              # Application entry point
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## 🛠️ Installation

### Prerequisites

- Python 3.9+
- MySQL (or SQLite for development)
- Redis (optional, for Celery tasks)

### Setup Steps

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd fastapi-demo
   ```

2. **Create virtual environment**

   ```bash
   python -m venv venv

   # Windows
   venv\Scripts\activate

   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**

   Create a `.env` file in the project root:

   ```env
   # Database Configuration
   MYSQL_HOST=localhost
   MYSQL_PORT=3306
   MYSQL_USER=root
   MYSQL_PASSWORD=your_password
   MYSQL_DB=your_database

   # Application Configuration
   LOG_LEVEL=INFO
   APP_DEBUG=false
   ```

5. **Run the application**

   ```bash
   uvicorn main:app --reload
   ```

   The API will be available at `http://localhost:8000`

## 📚 API Documentation

Once the server is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔌 API Endpoints

All endpoints are prefixed with `/api/v1/`

### Albums

| Method | Endpoint              | Description                 |
| ------ | --------------------- | --------------------------- |
| POST   | `/api/v1/albums`      | Create a new album          |
| GET    | `/api/v1/albums`      | List all albums (paginated) |
| GET    | `/api/v1/albums/{id}` | Get album by ID             |
| PUT    | `/api/v1/albums/{id}` | Update album                |
| DELETE | `/api/v1/albums/{id}` | Delete album                |

### Songs

| Method | Endpoint                         | Description                |
| ------ | -------------------------------- | -------------------------- |
| POST   | `/api/v1/songs`                  | Create a new song          |
| GET    | `/api/v1/songs`                  | List all songs (paginated) |
| GET    | `/api/v1/songs/{id}`             | Get song by ID             |
| GET    | `/api/v1/songs/album/{album_id}` | Get songs by album         |
| PUT    | `/api/v1/songs/{id}`             | Update song                |
| DELETE | `/api/v1/songs/{id}`             | Delete song                |

### Items

| Method | Endpoint             | Description       |
| ------ | -------------------- | ----------------- |
| POST   | `/api/v1/items`      | Create a new item |
| GET    | `/api/v1/items`      | List all items    |
| GET    | `/api/v1/items/{id}` | Get item by ID    |
| PUT    | `/api/v1/items/{id}` | Update item       |
| DELETE | `/api/v1/items/{id}` | Delete item       |

### Teams

| Method | Endpoint             | Description                |
| ------ | -------------------- | -------------------------- |
| POST   | `/api/v1/teams`      | Create a new team          |
| GET    | `/api/v1/teams`      | List all teams (paginated) |
| GET    | `/api/v1/teams/{id}` | Get team by ID             |
| PUT    | `/api/v1/teams/{id}` | Update team                |
| DELETE | `/api/v1/teams/{id}` | Delete team                |

## 📝 Response Format

All API responses follow a standardized format:

### Success Response

```json
{
  "code": 0,
  "message": "请求成功",
  "data": {
    "items": [...],
    "total": 100
  },
  "timestamp": 1729260645
}
```

### Error Response

```json
{
  "code": 4004,
  "message": "资源不存在",
  "data": null,
  "errors": {
    "message": "详细错误信息"
  },
  "timestamp": 1729260645
}
```

## 🎯 Business Codes

### Success Codes (2xxx)

- `2000` - Request successful
- `2001` - Created successfully
- `2004` - Deleted successfully
- `2005` - Updated successfully

### Client Error Codes (4xxx)

- `4000` - Bad request
- `4001` - Unauthorized
- `4003` - Forbidden
- `4004` - Not found
- `4101` - Invalid pagination parameters

### Server Error Codes (5xxx)

- `5000` - Internal server error
- `5100` - Database error
- `5102` - Database deletion failed
- `5103` - Database update failed
- `5104` - Database creation failed

## 🔧 Development

### Running Tests

```bash
# Add your test command here
pytest
```

### Code Quality

```bash
# Type checking
mypy .

# Linting
flake8 .

# Formatting
black .
```

### Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head
```

## 🐳 Docker Support

```dockerfile
# Dockerfile example
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 📖 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License.

## 👤 Author

Your Name - [Your GitHub Profile](https://github.com/yourusername)

## 🙏 Acknowledgments

- FastAPI framework and community
- SQLAlchemy async support
- All contributors and maintainers
