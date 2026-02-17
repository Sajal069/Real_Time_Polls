# Appylo - Real-Time Poll Rooms

Full-stack implementation of the `Real-Time Poll Rooms` assignment using Flask (API + sockets) and Next.js (responsive UI).

## Stack

- Backend: Flask, Flask-SocketIO, SQLAlchemy, SQLite
- Frontend: Next.js (App Router), React, TypeScript, socket.io-client
- Persistence: SQLite file (`backend/data/polls.db`)

## Assignment Coverage

1. Poll creation
- Create poll with question and at least 2 options
- Validation for empty/duplicate options and length bounds

2. Shareable links
- Polls are addressable at `/poll/<poll_id>`
- Backend returns canonical share URL based on `FRONTEND_BASE_URL`

3. Real-time vote updates
- Clients join socket room `poll:<poll_id>`
- Vote commits emit `poll_updated` to all connected viewers
- No page refresh required

4. Fairness / anti-abuse (2 mechanisms)
- Mechanism A: one vote per signed browser token (cookie) per poll
- Mechanism B: one vote per salted IP hash per poll
- Both are enforced with DB uniqueness constraints and pre-checks

5. Persistence
- Polls and votes are saved in SQLite
- Refresh/reopen keeps state intact

6. Responsive UI
- Mobile + desktop layout with adaptive controls

## Project Structure

- `backend/` Flask API + websocket server
- `frontend/` Next.js app

## Local Run

### 1) Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python run.py
```

Backend starts on `http://localhost:5000`.

### 2) Frontend

```bash
cd frontend
npm install
copy .env.local.example .env.local
npm run dev
```

Frontend starts on `http://localhost:3000`.

## API Endpoints

- `POST /api/polls` create poll
- `GET /api/polls/<poll_id>` fetch poll + viewer vote state
- `POST /api/polls/<poll_id>/vote` submit vote
- `GET /health` health check

## Edge Cases Handled

- Empty question/options
- Less than 2 options
- Duplicate options
- Invalid option id vote
- Duplicate vote attempts by browser token
- Duplicate vote attempts by IP hash
- Poll not found

## Known Limitations

- IP-based control can block distinct users behind same NAT/public IP
- Cookie-based control can be bypassed with manual cookie/device reset
- No authentication; this is intentionally lightweight for assignment scope
- No rate limiting yet (can be added as additional hardening)
