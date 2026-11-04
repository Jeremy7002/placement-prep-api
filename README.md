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
DATABASE_URL_TEST=mysql+pymysql://<user>:<password>@<host>:<port>/<test_db>?ssl_ca=./certs/ca.pem
```
 
**3. Run**
 
```bash
uvicorn main:app --reload
```
 
Open http://localhost:8000/docs for interactive API docs.
 
## Architecture
 
**Service Layer:** Business logic for problems, companies and resources lives in services; routes only receive and return data. Auth is the exception — register and login sit in `routers/auth.py`, with the reusable pieces (`hash_password`, `verify_password`, `create_access_token`, `get_current_user`) in `security.py`.

 
**User Isolation:** Every table has a `user_id` foreign key. Queries always filter by the authenticated user's ID — no cross-user data leaks.
 
**JWT Flow:** Register → Login (get token) → Include token in `Authorization: Bearer <token>` header → The `get_current_user` dependency validates the token and loads the user → Service queries with that user's ID.
  
## API Endpoints

**Auth**
- `POST /auth/register` — Create account
- `POST /auth/login` — Get JWT token

**Users** (protected)
- `GET /users/me` — The authenticated user's own record

**Problems** (protected)
- `POST /problems` — Create problem record
- `GET /problems` — List your problems (`?topic=` and `?status=` filters)
- `PUT /problems/{id}` — Update status or date solved
- `DELETE /problems/{id}` — Delete problem

**Resources** (protected)
- `POST /resources` — Create resource
- `GET /resources` — List your resources
- `DELETE /resources/{id}` — Delete resource

**Companies** (protected)
- `POST /companies` — Create company
- `GET /companies` — List your companies
- `PUT /companies/{id}` — Update role, format or status
- `DELETE /companies/{id}` — Delete company

**Analytics** (protected)
- `GET /analytics/progress` — Weekly problems solved
- `GET /analytics/weak-topics` — Solve rate per topic

Full docs at `/docs` when running locally.
 
## Testing
 
```bash
pytest -v
```
 
28 tests cover auth, CRUD operations, user isolation, and analytics.
 
## Production Notes
 
- Render free tier spins down after 15 minutes of inactivity — first request afterward may take 30–60 seconds.
- TiDB Cloud free tier uses distributed ID allocation, so IDs are unique but not strictly sequential.
 