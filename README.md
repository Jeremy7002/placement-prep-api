# Placement Prep API

A backend REST API built to track and organize placement preparation activity — coding problems solved, learning resources, and company application progress — for students preparing for technical interviews and campus placements. Built with FastAPI and SQLAlchemy, using JWT-based authentication to keep each user's data private and secure. The API supports full CRUD operations across problems, resources, and company applications, along with analytics endpoints that surface progress trends and topic-level performance insights. Developed in seven structured phases — from core models and authentication through input validation, error handling, and production deployment.

## Architecture

The API is deployed across two independent free-tier services: [Render](https://render.com) hosts the application itself, and [TiDB Cloud](https://tidbcloud.com) hosts the database. Railway was initially considered for combined app-and-database hosting, but its free trial requires a credit card, so Render and TiDB Cloud were chosen instead — a genuinely free, no-card combination that still uses production-style infrastructure rather than a local-only setup. TiDB is MySQL-compatible, so the existing SQLAlchemy models and PyMySQL driver required no changes.

Connections to TiDB are secured over TLS using a CA certificate, since the database is reachable over TiDB's public endpoint.

**Note:** the app is hosted on Render's free tier, which spins down after 15 minutes of inactivity. The first request after a period of idle time may take 30-60 seconds to respond while the instance restarts — this is expected behavior, not an error.

## Setup Instructions

**Prerequisites**
- Python 3.12
- A MySQL-compatible database (this project uses [TiDB Cloud](https://tidbcloud.com)'s free tier)

**1. Clone the repository**

```
git clone https://github.com/Jeremy7002/placement-prep-api.git
cd placement-prep-api
```

**2. Create and activate a virtual environment**

```
python -m venv venv
```

On Windows:

```
venv\Scripts\activate
```

On macOS/Linux:

```
source venv/bin/activate
```

**3. Install dependencies**

```
pip install -r requirements.txt
```

**4. Set up environment variables**

Create a `.env` file in the project root with the following variables:

```
SECRET_KEY=your_jwt_secret_key_here
DATABASE_URL=mysql+pymysql://<username>:<password>@<host>:<port>/<database>?ssl_ca=./certs/ca.pem
```

If using TiDB Cloud, download your CA certificate from your cluster's "Connect" page and place it at `certs/ca.pem` in the project root.

**5. Run the application**

```
uvicorn main:app --reload
```

**Note (Windows):** if the above command isn't recognized after activating the virtual environment, run it explicitly instead:

```
venv\Scripts\python.exe -m uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`, with interactive documentation at `http://localhost:8000/docs`. Database tables are created automatically on first run.

## API Documentation

Full interactive documentation is available at [`/docs`](https://placement-prep-api.onrender.com/docs) via Swagger UI. Below are examples of core endpoints.

### Register a new user

`POST /auth/register`

**Request body:**

```json
{
  "email": "user@example.com",
  "password": "yourpassword"
}
```

**Response** (`201 Created`):

```json
{
  "id": 1,
  "email": "user@example.com"
}
```

### Login

`POST /auth/login`

**Request body:**

```json
{
  "email": "user@example.com",
  "password": "yourpassword"
}
```

**Response** (`200 OK`):

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

Use the returned `access_token` as a Bearer token in the `Authorization` header for all protected routes below.

### Create a problem (protected)

`POST /problems?topic={topic}&title={title}&difficulty={difficulty}&status={status}&date_solved={date_solved}`

**Requires:** `Authorization: Bearer <access_token>`

**Query parameters:**
- `topic` (string)
- `title` (string)
- `difficulty` (string) — valid choices: `Easy`, `Medium`, `Hard`
- `status` (string) — valid choices: `Completed`, `Not Completed`, `Pending`
- `date_solved` (date) — format: `YYYY-MM-DD`

**Response** (`201 Created`):

```json
{
  "id": 1,
  "title": "Two Sum"
}
```

### Weekly progress analytics (protected)

`GET /analytics/progress`

**Requires:** `Authorization: Bearer <access_token>`

**Response** (`200 OK`):

```json
[
  {
    "week_start": "2026-06-30",
    "problems_solved": 4
  }
]
```