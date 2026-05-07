# HotelSearcher (PackHotelsBack)

HotelSearcher is a backend application designed to track hotel room availability and pricing based on user-defined geographical search points. It utilizes FastAPI for the web interface, PostgreSQL for data persistence, and Celery with Redis for asynchronous background tasks and periodic parsing.

## 🚀 Features

- **User Authentication**: Secure JWT-based authentication system (Login/Register).
- **Search Points**: Define search areas by coordinates (longitude, latitude) and radius.
- **Automated Hotel Discovery**: Background tasks automatically find hotels within the specified radius of a search point.
- **Periodic Room Availability Tracking**: Automatically parses and updates room availability and pricing every 3 minutes for all tracked hotels.
- **Data Persistence**: Stores history of room availability and pricing for analysis.
- **Async Processing**: Offloads heavy parsing tasks to Celery workers.
- **Monitoring**: Integrated with Cronitor for task monitoring.

## 🛠 Tech Stack

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **Database**: [PostgreSQL](https://www.postgresql.org/)
- **ORM**: [SQLAlchemy 2.0](https://www.sqlalchemy.org/)
- **Migrations**: [Alembic](https://alembic.sqlalchemy.org/)
- **Task Queue**: [Celery](https://docs.celeryq.dev/)
- **Broker**: [Redis](https://redis.io/)
- **Geocoding**: [Geopy](https://geopy.readthedocs.io/)
- **Containerization**: [Docker](https://www.docker.com/) & [Docker Compose](https://docs.docker.com/compose/)

## 📁 Project Structure

```text
├── api/                # FastAPI handlers and Pydantic models
│   ├── actions/        # Business logic for auth and security
│   ├── handlers.py     # User and search related endpoints
│   ├── hotel_handlers.py # Hotel management endpoints
│   └── models.py       # Pydantic schemas
├── db/                 # Database configuration and models
│   ├── dals.py         # Data Access Layer (Repository pattern)
│   ├── models.py       # SQLAlchemy models
│   └── session.py      # Database session management
├── migrations/         # Alembic migration scripts
├── tasks/              # Celery tasks and parser logic
│   ├── parser.py       # Scraper/Parser implementation
│   ├── tasks.py        # Celery task definitions
│   └── dals.py         # DALs for background tasks
├── main.py             # Application entry point
├── settings.py         # Configuration management
└── docker-compose.yml  # Deployment configuration
```

## ⚙️ Setup & Installation

### Prerequisites

- Python 3.10+
- Docker & Docker Compose
- Redis (if running locally without Docker)
- PostgreSQL (if running locally without Docker)

### Environment Variables

Create a `.env` file in the root directory (refer to `settings.py` for all options):

```env
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REAL_DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/dbname
REAL_DATABASE_URL_CEL=postgresql://user:pass@localhost:5432/dbname
REDIS_BROKER_URL=redis://localhost:6379/0
CRONITOR_API_KEY=your_cronitor_key
```

### Running with Docker

The easiest way to get started is using the provided `Makefile`:

```bash
# Start all services
make up

# Stop all services
make down
```

Or directly via Docker Compose:

```bash
docker compose -f docker-compose-local.yml up -d
```

### Manual Local Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run migrations**:
   ```bash
   alembic upgrade head
   ```

3. **Start the API**:
   ```bash
   uvicorn main:app --reload
   ```

4. **Start Celery Worker**:
   ```bash
   celery -A tasks.tasks worker --loglevel=INFO -P solo
   ```

5. **Start Celery Beat**:
   ```bash
   celery -A tasks.tasks beat --loglevel=INFO
   ```

## 🔍 API Endpoints

- **POST `/login/token`**: Authenticate and get JWT token.
- **POST `/user/`**: Register a new user.
- **POST `/search/`**: Create a new search point (triggers hotel parsing).
- **GET `/search/`**: List user's search points and discovered hotels.
- **GET `/hotel/`**: Get detailed information and room statistics for a specific hotel.

For full interactive documentation, visit `http://localhost:8000/docs` once the server is running.

## 🤖 Background Tasks

- `parse_hotels(search_id)`: Triggered when a new search point is created. Finds hotels near the coordinates.
- `parse_rooms()`: Runs every 3 minutes via Celery Beat. Updates availability for all discovered hotels.

---
Developed as a project for hotel tracking and availability analysis.
