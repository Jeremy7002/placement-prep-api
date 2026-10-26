# Placement Prep API
 
A REST API for tracking placement preparation — coding problems solved, learning resources, and company applications. Built with FastAPI and SQLAlchemy using JWT authentication to isolate each user's data. Supports full CRUD operations across problems, resources, and companies, plus analytics endpoints for progress tracking.
 
Deployed on Render (app) and TiDB Cloud (MySQL-compatible database).
 
## Stack
 
- **Framework:** FastAPI
- **Database:** MySQL (TiDB Cloud)
- **ORM:** SQLAlchemy
- **Auth:** JWT (HS256)
- **Testing:** pytest (28 tests)
## Setup
 
**Prerequisites:** Python 3.12, MySQL-compatible database
 
**1. Clone and setup**
 
```bash
git clone https://github.com/Jeremy7002/placement-prep-api.git
cd placement-prep-api
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```
 
**2. Environment variables**
 
Create `.env`:
 
```
SECRET_KEY=your_jwt_secret_key
DATABASE_URL=mysql+pymysql://<user>:<password>@<host>:<port>/<db>?ssl_ca=./certs/ca.pem
```
 
**3. Run**
 
```bash
uvicorn main:app --reload
```
 
Open http://localhost:8000/docs for interactive API docs.
 
## Architecture
 
**Service Layer:** All business logic (auth, validation, user isolation) lives in services. Routes only receive and return data.
 
**User Isolation:** Every table has a `user_id` foreign key. Queries always filter by the authenticated user's ID — no cross-user data leaks.
 
**JWT Flow:** Register → Login (get token) → Include token in `Authorization: Bearer <token>` header → Middleware validates token and extracts user ID → Service queries with that user ID.
 
## API Endpoints
 
**Auth**
- `POST /auth/register` — Create account
- `POST /auth/login` — Get JWT token
**Problems** (protected)
- `POST /problems` — Create problem record
- `GET /problems` — List your problems
- `GET /problems/{id}` — Get one problem
- `PUT /problems/{id}` — Update problem
- `DELETE /problems/{id}` — Delete problem
**Analytics** (protected)
- `GET /analytics/progress` — Weekly problems solved
- `GET /analytics/weak-topics` — Topics with lowest solve rate
Full docs at `/docs` when running locally.
 
## Testing
 
```bash
pytest -v
```
 
28 tests cover auth, CRUD operations, user isolation, and analytics.
 
## Production Notes
 
- Render free tier spins down after 15 minutes of inactivity — first request afterward may take 30–60 seconds.
- TiDB Cloud free tier uses distributed ID allocation, so IDs are unique but not strictly sequential.
 