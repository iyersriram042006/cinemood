# CineMood

A mood-aware movie journal and social discovery application for recording watched films, understanding personal viewing patterns, and finding movies that match the language of your mood.

## 🌐 Live Demo

**Live Application:**  
https://cinemood-frontend.onrender.com

**Backend API:**  
https://cinemood-backend-lyv3.onrender.com

The application is deployed on **Render**. The frontend can be opened directly through the live application URL without performing the local installation steps below.

## Overview

CineMood combines a personal movie journal with lightweight, explainable recommendation logic and social features. Authenticated users can search for films through TMDB, record ratings, reviews, watch dates, rewatch status, and mood tags, then review aggregate statistics about their viewing history.

The recommendation experience accepts free-form mood text such as “I’m bored, want something light”. The backend tokenizes that text, removes a small set of stopwords, and scores the user’s previously journaled movies using overlapping mood tags, review words, genres, and the user’s rating. If no direct match is found, CineMood returns the user’s highest-rated logged movies instead.

Users can also add friends, accept or reject requests, view a friend’s public journal, like and comment on journal entries, and compare shared movies and genre counts. Movie metadata is fetched from TMDB and persisted in PostgreSQL through SQLAlchemy.

## Problem Statement

Choosing a movie can be difficult when a user knows the kind of experience they want but cannot name a specific title. CineMood addresses this by letting users describe a mood in natural language and comparing that text with the mood tags, reviews, and genres already present in their own journal.

It also addresses the related need to keep a structured record of watched movies. Rather than treating recommendations as a standalone catalog search, CineMood uses the user’s recorded viewing history and ratings as the basis for matching and fallback results.

## Solution

CineMood follows this flow:

```text
User signs up or logs in
        ↓
React frontend stores the bearer token
        ↓
FastAPI validates the token and loads the user
        ↓
Journal, analytics, social, or recommendation endpoint executes
        ↓
PostgreSQL data and/or TMDB metadata are read or updated
        ↓
JSON response is returned to the frontend
        ↓
React page renders the journal, insights, recommendations, or social view
```

## Key Features

- **Account authentication** — Email/password signup and login issue seven-day JWT bearer tokens. Passwords are hashed with bcrypt before storage.
- **TMDB movie search** — Search results come from TMDB’s `/search/movie` endpoint and expose title, release date, poster path, rating, and overview.
- **Personal movie journal** — Log a movie with a 0–5 rating, review, watched date, rewatch flag, and comma-separated mood tags. Journal entries can be listed, updated through the API, and deleted.
- **Mood-based recommendations** — Free-form mood text is matched against journal mood tags, review words, and movie genre words, with a rating boost and a top-rated fallback.
- **Viewing analytics** — The dashboard exposes total watched movies, movies watched this year, average rating, rewatches, genre statistics, frequently logged directors, rating distribution, timeline data, and a generated text summary.
- **Friend network** — Send requests by email, accept or reject incoming requests, list accepted friends, and remove friendships through the backend API.
- **Social journal interactions** — Authenticated users can view a user’s public journal, toggle likes on entries, and post or read comments.
- **Taste comparison** — Compare two users’ shared movies, ratings, rating differences, and top genre overlap.
- **Protected frontend routes** — Journal, dashboard, recommendations, friends, profiles, and comparisons require a token; unauthenticated visitors are redirected to `/login`.

## System Architecture

```mermaid
flowchart TD
    U[User] --> F[React 19 + Vite frontend]
    F -->|Axios JSON requests| A[FastAPI application]
    F -->|Bearer token in Authorization header| A
    A --> AUTH[JWT and bcrypt authentication]
    A --> DB[(PostgreSQL via SQLAlchemy)]
    A --> TMDB[TMDB API]
    A --> REC[Keyword and score recommendation service]
    A --> ANALYTICS[Analytics and taste comparison logic]
    A --> SOCIAL[Friends, likes, comments, public journals]
    TMDB --> DB
    DB --> REC
    DB --> ANALYTICS
    DB --> SOCIAL
    A -->|JSON responses| F
```

### Runtime components

- **Frontend:** `frontend/` is a React single-page application bootstrapped by Vite. `BrowserRouter` defines the application routes and `AuthContext` manages the token in browser `localStorage`.
- **Backend:** `backend/app/main.py` creates the FastAPI app, enables CORS for the local Vite origin and deployed frontend, creates SQLAlchemy tables at startup, and registers the API routers.
- **Persistence:** `backend/app/core/database.py` reads `DATABASE_URL`, creates an SQLAlchemy engine/session factory, and supplies request-scoped sessions.
- **Movie data:** `backend/app/services/tmdb_service.py` calls TMDB using a bearer token from `TMDB_API_KEY`. Selected movie details are cached in the `movies` table when journal entries or explicit movie-add operations require them.
- **Recommendation processing:** `backend/app/services/recommendation_service.py` performs deterministic keyword matching over the current user’s existing journal entries; no trained model or LLM is used.

## Application Workflow

1. A visitor opens the frontend and chooses **Login** or **Sign Up**.
2. The frontend posts credentials to `/api/auth/login` or `/api/auth/signup`.
3. The backend validates the request, hashes/verifies the password, creates a JWT, and returns `access_token` with `token_type: "bearer"`.
4. `AuthContext` stores the token in `localStorage`; Axios adds it to subsequent requests.
5. On the Journal page, the user searches for a title. The backend forwards the query to TMDB and returns up to the results supplied by TMDB.
6. The user selects a movie and submits rating, review, date, rewatch status, and mood tags. The backend retrieves full TMDB details if the movie is not already stored, creates normalized mood tags, and saves the journal entry.
7. Dashboard requests calculate statistics directly from the authenticated user’s entries.
8. Recommendation requests tokenize the supplied mood, score matching journaled movies, sort by score, and return explanations; an empty match set falls back to highest-rated entries.
9. Social pages use friendship, public-journal, like, comment, and comparison endpoints to display connected users’ activity.

## Technology Stack

| Layer | Technology | Purpose |
| --- | --- | --- |
| Frontend | React `^19.2.8` | Single-page user interface |
| Frontend tooling | Vite `^8.3.0` | Development server and production bundling |
| Routing | React Router DOM `^7.18.4` | Client-side routes and protected-route redirects |
| HTTP client | Axios `^1.20.0` | Frontend-to-backend API requests and auth header injection |
| Backend | FastAPI `0.128.5` | REST API and request validation |
| Runtime server | Uvicorn `0.40.0` | ASGI server used by the backend Procfile |
| ORM | SQLAlchemy `2.0.54` | PostgreSQL access and model mapping |
| Database | PostgreSQL | Users, movies, journal entries, moods, friendships, likes, and comments |
| Authentication | `python-jose`, bcrypt | JWT access tokens and password hashing |
| External API | TMDB v3 | Movie search and movie details/credits |
| Deployment | Render | Separate frontend and backend services, as reflected by the supplied live URLs |

CineMood does **not** implement a machine-learning model, embeddings pipeline, LLM integration, or vector search. Its recommendation feature is rule-based keyword scoring over a user’s own journal data.

## Project Structure

```text
cinemood/
├── backend/
│   ├── Procfile                    # Render/Heroku-style Uvicorn process command
│   ├── requirements.txt            # Pinned Python dependencies
│   └── app/
│       ├── main.py                 # FastAPI app, CORS, table initialization, routers
│       ├── api/                    # Auth, movies, journal, analytics, recommendations, social routes
│       ├── core/
│       │   ├── database.py         # DATABASE_URL, engine, sessions, declarative Base
│       │   ├── deps.py             # Current-user dependency
│       │   └── security.py         # bcrypt and JWT helpers
│       ├── models/models.py        # SQLAlchemy models and relationships
│       ├── schemas/                # Pydantic request/response models
│       └── services/
│           ├── recommendation_service.py
│           └── tmdb_service.py
├── frontend/
│   ├── package.json                # Scripts and React/Vite dependencies
│   ├── vite.config.js              # Vite React plugin configuration
│   ├── index.html                  # Browser entry point
│   └── src/
│       ├── App.jsx                 # Router and protected routes
│       ├── main.jsx                # React root
│       ├── components/Navbar.jsx
│       ├── context/AuthContext.jsx
│       ├── pages/                  # Auth, Journal, Dashboard, Recommendations, Friends, Compare
│       └── services/api.js          # Axios client and endpoint wrappers
└── .gitignore
```

## Frontend

The frontend uses React with JSX and Vite. `src/main.jsx` mounts `App` inside `StrictMode`; `src/App.jsx` wraps the application in `AuthProvider`, renders the authenticated navigation bar, and defines these routes:

| Route | Page | Access |
| --- | --- | --- |
| `/login` | `Auth.jsx` | Public |
| `/` | `Journal.jsx` | Authenticated |
| `/dashboard` | `Dashboard.jsx` | Authenticated |
| `/recommendations` | `Recommendations.jsx` | Authenticated |
| `/friends` | `Friends.jsx` | Authenticated |
| `/profile/:userId` | `FriendProfile.jsx` | Authenticated |
| `/compare/:userId` | `Compare.jsx` | Authenticated |

`AuthContext.jsx` owns login, signup, logout, and the `isAuthenticated` flag. `services/api.js` creates an Axios client whose base URL is `VITE_API_URL` or `http://127.0.0.1:8000`, and an interceptor adds `Authorization: Bearer <token>` when a token exists.

The pages are intentionally small and request data directly through service wrappers. Styling is primarily implemented with inline styles plus `src/App.css` and `src/index.css`; there is no component library or global state library in the dependency manifest.

## Backend

The backend is a FastAPI application with routers grouped by responsibility:

- `api/auth.py` handles signup and login.
- `api/movies.py` searches TMDB and persists movie details.
- `api/journal.py` creates, lists, updates, and deletes authenticated journal entries.
- `api/analytics.py` calculates overview, genre, director, rating, timeline, and summary data.
- `api/recommendations.py` delegates mood matching to `recommendation_service.py`.
- `api/friends.py` manages friend requests and accepted friendships.
- `api/social.py` exposes public journals, likes, and comments.
- `api/compare.py` compares the current user’s entries with another user’s entries.

Protected routes use `get_current_user` from `core/deps.py`. It decodes the bearer JWT, reads the `sub` user ID, and loads the corresponding `User` row. `main.py` allows requests from `http://localhost:5173` and `https://cinemood-frontend.onrender.com`, permits credentials, methods, and headers, and registers all routers.

Tables are created at import/startup time with `Base.metadata.create_all(bind=engine)`. No Alembic migration files or migration configuration are present in the repository.

## API Documentation

The backend base URL is `https://cinemood-backend-lyv3.onrender.com` in the deployed environment. Unless noted otherwise, endpoints requiring a current user expect an `Authorization: Bearer <JWT>` header.

### General and authentication

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| GET | `/` | No | Returns `{ "message": "CineMood API running" }`. |
| POST | `/api/auth/signup` | No | Creates a user from `email`, `password`, and optional `name`; returns an access token. |
| POST | `/api/auth/login` | No | Verifies `email` and `password`; returns an access token. |

### Movies and journal

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| GET | `/api/movies/search?query={text}` | No | Searches TMDB movie titles. An empty query returns `400`. |
| POST | `/api/movies/{tmdb_id}` | No | Adds a TMDB movie to the local database if it is not already stored. |
| POST | `/api/journal` | Yes | Creates a journal entry and fetches movie details from TMDB when needed. |
| GET | `/api/journal` | Yes | Lists the current user’s entries, newest watched date first. |
| PUT | `/api/journal/{entry_id}` | Yes | Updates supplied rating, review, date, rewatch flag, or moods. |
| DELETE | `/api/journal/{entry_id}` | Yes | Deletes one of the current user’s entries. |

Journal creation accepts this shape:

```json
{
  "tmdb_id": 550,
  "rating": 4.5,
  "review": "A memorable rewatch",
  "watched_at": "2026-09-18",
  "is_rewatch": false,
  "moods": ["comfort", "thought-provoking"]
}
```

### Analytics and recommendations

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| GET | `/api/analytics/overview` | Yes | Returns total movies, current-year movies, average rating, and rewatch count. |
| GET | `/api/analytics/genres` | Yes | Returns genre counts and average ratings. |
| GET | `/api/analytics/directors` | Yes | Returns the ten most frequently logged directors. |
| GET | `/api/analytics/ratings` | Yes | Returns rating distribution data. |
| GET | `/api/analytics/timeline` | Yes | Returns monthly watched-entry counts. |
| GET | `/api/analytics/summary` | Yes | Returns a generated text summary based on entries and genres. |
| POST | `/api/recommendations` | Yes | Accepts `{ "mood": "...", "limit": 10 }` and returns scored journaled movies. |

A recommendation response has the form:

```json
{
  "query": "something relaxing",
  "recommendations": [
    {
      "movie_id": "movie-uuid",
      "title": "Example Movie",
      "poster_path": "/example.jpg",
      "rating": 4.5,
      "moods": ["relaxing"],
      "score": 1.25,
      "reason": "tagged as relaxing; genre match: ..."
    }
  ]
}
```

### Friends and social features

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| POST | `/api/friends/request` | Yes | Sends a request using `{ "addressee_email": "friend@example.com" }`. |
| POST | `/api/friends/{friendship_id}/accept` | Yes | Accepts an incoming request. |
| POST | `/api/friends/{friendship_id}/reject` | Yes | Rejects an incoming request. |
| GET | `/api/friends` | Yes | Lists accepted friends. |
| GET | `/api/friends/pending` | Yes | Lists pending incoming requests. |
| DELETE | `/api/friends/{friendship_id}` | Yes | Removes a friendship. |
| POST | `/api/social/entries/{entry_id}/like` | Yes | Toggles the current user’s like and returns `liked`. |
| POST | `/api/social/entries/{entry_id}/comments` | Yes | Adds a comment using `{ "text": "..." }`. |
| GET | `/api/social/entries/{entry_id}/comments` | No | Lists comments for an entry. |
| GET | `/api/social/users/{user_id}/journal` | Yes | Returns a user’s journal entries with like/comment counts. |
| GET | `/api/compare/{other_user_id}` | Yes | Compares shared movies, ratings, and genre counts with another user. |

FastAPI also exposes its generated interactive documentation at `/docs` when the backend is running.

## Database

CineMood uses PostgreSQL through SQLAlchemy. `DATABASE_URL` is loaded with `python-dotenv`, passed directly to `create_engine`, and used to create request sessions. On application startup, `Base.metadata.create_all(bind=engine)` creates any missing tables.

### Entities

- **`users`** — UUID, unique email, display name, bcrypt password hash, creation timestamp.
- **`movies`** — UUID, unique TMDB ID, titles, overview, poster/backdrop paths, release date, runtime, JSONB genres/directors/cast, and TMDB vote data.
- **`mood_tags`** — normalized, unique mood names.
- **`journal_entries`** — user/movie foreign keys, rating, review, watched date, rewatch fields, optional embedding text, and timestamps.
- **`journal_entry_moods`** — many-to-many join table between journal entries and mood tags.
- **`friendships`** — requester/addressee user IDs and `pending`, `accepted`, or `rejected` status.
- **`likes`** — user-to-journal-entry likes.
- **`comments`** — user-to-journal-entry comments with text and timestamp.

```mermaid
erDiagram
    USER ||--o{ JOURNAL_ENTRY : records
    MOVIE ||--o{ JOURNAL_ENTRY : appears_in
    JOURNAL_ENTRY }o--o{ MOOD_TAG : tagged_with
    USER ||--o{ FRIENDSHIP : requests
    USER ||--o{ LIKE : creates
    JOURNAL_ENTRY ||--o{ LIKE : receives
    USER ||--o{ COMMENT : writes
    JOURNAL_ENTRY ||--o{ COMMENT : receives
```

The SQLAlchemy model declares the core foreign keys and relationships. The repository does not include migration scripts, seed data, or a committed database schema dump.

## External APIs & Services

### TMDB

CineMood uses **The Movie Database API v3** for movie search and details. `tmdb_service.py` sends requests to `https://api.themoviedb.org/3` with an `Authorization: Bearer <TMDB_API_KEY>` header. It calls:

- `/search/movie` for title search.
- `/movie/{tmdb_id}?append_to_response=credits` for detailed metadata, directors, and the first ten cast members.

Poster images are rendered by the frontend from TMDB’s image host using paths returned by the API, for example `https://image.tmdb.org/t/p/w92/{poster_path}`. A TMDB API key is required by the backend.

### Render

The supplied frontend and backend URLs indicate separate Render deployments. The backend repository configuration includes `backend/Procfile`:

```text
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

No `render.yaml` or Render service manifest is present in the repository, so exact dashboard settings, service plans, and the frontend service’s Render start configuration cannot be verified from source.

## Recommendation System

The recommendation system is deterministic and rule-based rather than AI/ML-based.

1. The user submits free-form `mood` text to `POST /api/recommendations`.
2. `_extract_keywords` lowercases the text, keeps alphabetic words, removes the hard-coded `STOPWORDS` set, and ignores words of length two or less.
3. The service loads the current user’s journal entries.
4. Each entry receives points for keyword overlap with:
   - Mood-tag words: `0.5` per overlapping word.
   - Review words: `0.3` per overlapping word.
   - Genre words: `0.2` per overlapping word.
   - Rating boost: `rating / 5 * 0.3`.
5. Entries with a score above zero are sorted in descending score order and truncated to `limit`.
6. If there are no scored entries, the service returns up to `limit` entries ordered by rating, with the reason `no direct mood match — showing your top-rated movies instead`.

Recommendations therefore come only from movies already present in the user’s journal. The implementation does not query TMDB for unseen recommendations and does not calculate embeddings despite the model containing an unused `embedding_text` column.

## Environment Variables

The repository does not include committed `.env.example` files. The following variables are read directly by the implementation:

| Variable | Required | Purpose |
| --- | --- | --- |
| `DATABASE_URL` | Yes | SQLAlchemy connection URL for PostgreSQL. |
| `SECRET_KEY` | Yes | Secret used to sign and decode HS256 JWTs. |
| `TMDB_API_KEY` | Yes for movie search/details | TMDB bearer token used by `tmdb_service.py`. |
| `VITE_API_URL` | No locally / Yes for a non-default frontend API host | Frontend Axios base URL. If unset, it defaults to `http://127.0.0.1:8000`. |
| `PORT` | Render-provided for backend | Port consumed by the Uvicorn Procfile command. |

Example backend environment configuration (use real values only in your local environment or deployment secret store):

```env
DATABASE_URL=postgresql://user:password@host:5432/cinemood
SECRET_KEY=replace_with_a_long_random_secret
TMDB_API_KEY=your_tmdb_bearer_token
```

Example frontend configuration:

```env
VITE_API_URL=http://127.0.0.1:8000
```

Do not commit real database credentials, JWT secrets, or TMDB keys.

## Prerequisites

- Git
- Python with `pip` (the repository does not specify a Python version)
- Node.js and npm compatible with the installed React/Vite dependencies
- A PostgreSQL database
- A TMDB API bearer token for movie search and metadata retrieval
- A long random `SECRET_KEY` for JWT signing

## Installation

Clone the repository and create separate environments for the backend and frontend:

```bash
git clone https://github.com/iyersriram042006/cinemood.git
cd cinemood
```

### Backend

```bash
cd backend
python -m venv .venv

# macOS/Linux
source .venv/bin/activate

# Windows PowerShell
# .venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

Set `DATABASE_URL`, `SECRET_KEY`, and `TMDB_API_KEY` in the backend process environment or in a local `backend/.env` file. `python-dotenv` loads `.env` values when the backend imports its database module.

### Frontend

```bash
cd ../frontend
npm install
```

For a local backend, `VITE_API_URL` may be omitted because the frontend defaults to `http://127.0.0.1:8000`. To use another backend, create `frontend/.env` with:

```env
VITE_API_URL=http://127.0.0.1:8000
```

Vite reads `VITE_*` variables at build time, so restart the dev server after changing them.

## Running Locally

Start the backend from the repository’s `backend` directory:

```bash
cd backend
# Activate .venv first
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Start the frontend in a second terminal:

```bash
cd frontend
npm run dev
```

The Vite development server normally serves the frontend at `http://localhost:5173`; the API is available at `http://127.0.0.1:8000`. The backend CORS configuration explicitly allows the Vite origin.

## Deployment

CineMood is deployed on **Render** as separate frontend and backend services.

### Frontend

**Live URL:**  
https://cinemood-frontend.onrender.com

The frontend is a Vite application. The verified package scripts are:

```bash
npm run build   # vite build
npm run preview # vite preview
```

Set `VITE_API_URL` to the deployed backend URL during the frontend build:

```env
VITE_API_URL=https://cinemood-backend-lyv3.onrender.com
```

The repository does not contain a Render manifest or a static-host configuration, so the exact Render dashboard build/publish settings are not verifiable from source. The deployed URL confirms that a Render frontend service exists.

### Backend

**Live URL:**  
https://cinemood-backend-lyv3.onrender.com

The backend runs as a Python ASGI service. Its committed process command is:

```text
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Install dependencies with `pip install -r requirements.txt`, configure `DATABASE_URL`, `SECRET_KEY`, and `TMDB_API_KEY` as Render environment variables, and ensure the working directory makes `app.main:app` importable (the committed `Procfile` is located in `backend/`). Exact Render build and working-directory settings are not committed, so they cannot be documented more precisely without access to the Render service configuration.

The backend CORS allowlist includes the deployed frontend URL. The frontend must be built with `VITE_API_URL=https://cinemood-backend-lyv3.onrender.com`; otherwise the client-side default points to a local API.

## Usage

To use the deployed application without local setup:

1. Open https://cinemood-frontend.onrender.com.
2. Create an account or log in with an existing account.
3. Search for a movie from **Journal**, select it, enter a rating, date, review, and optional mood tags, then add it.
4. Open **Dashboard** to see viewing totals, genre and director information, and the generated taste summary.
5. Open **Recommendations**, describe the mood or type of viewing experience you want, and submit the form.
6. Use **Friends** to send requests by email, manage incoming requests, view a friend’s journal, and compare taste.
7. From a friend’s journal, like entries or open the comment area to read and post comments.

## Screenshots / Demo Assets

No screenshots, GIFs, or video demo assets were found in the repository. The live frontend URL above is the available demonstration of the deployed application.

## Testing

No automated test files or test-runner configuration were found in the repository. The frontend package provides `npm run lint`, which runs Oxlint, but there is no committed test script. Backend verification is currently manual through the running FastAPI application and its `/docs` interface.

## Build

### Frontend production build

```bash
cd frontend
npm run build
```

This runs `vite build` and produces the Vite production output in `frontend/dist/`.

### Backend

The backend has no separate compilation step. Render installs `backend/requirements.txt` and starts the FastAPI application using the Uvicorn command in `backend/Procfile`.

## Troubleshooting

### Frontend requests the wrong API

Set `VITE_API_URL` before starting or building the frontend. If it is unset, `frontend/src/services/api.js` uses `http://127.0.0.1:8000`. Restart Vite after changing environment variables.

### Backend cannot connect to the database

Verify that `DATABASE_URL` is set and points to a reachable PostgreSQL instance. The backend creates its SQLAlchemy engine during import, so a missing or invalid URL prevents startup.

### Authentication fails after changing secrets

JWTs are signed with `SECRET_KEY` and expire after seven days. Changing the key invalidates existing tokens; log in again after updating it.

### Movie search or journal creation fails

Verify `TMDB_API_KEY` and confirm that the backend can reach `https://api.themoviedb.org/3`. TMDB request errors are raised by the service and can surface as backend errors.

### Browser reports a CORS error

For local development, use the Vite origin `http://localhost:5173`, which is in the backend allowlist. For production, ensure the request originates from `https://cinemood-frontend.onrender.com` and that the frontend was built with the deployed backend URL.

### Tables are missing

The application calls `Base.metadata.create_all` at startup. Ensure the database user has permission to create tables. There are no Alembic migrations in this repository.

## Security

- Keep `DATABASE_URL`, `SECRET_KEY`, and `TMDB_API_KEY` outside source control.
- Passwords are stored as bcrypt hashes rather than plaintext.
- Authenticated API routes use JWT bearer authentication and load the user from the token subject.
- The frontend stores the JWT in browser `localStorage`; this is convenient for the current SPA but should be evaluated against an application’s XSS threat model.
- CORS is restricted to the configured local frontend origin and deployed frontend origin in `main.py`.
- The repository does not include a dedicated rate limiter, refresh-token mechanism, security headers configuration, or automated security test suite.

## Future Improvements

### Currently implemented

- JWT login and signup with bcrypt password hashing.
- TMDB-backed search and movie metadata persistence.
- Journal, analytics, deterministic mood matching, friendship, social, and comparison workflows.

### Potential future improvements

- Add Alembic migrations and explicit database deployment/rollback workflows.
- Add automated backend API tests and frontend component/integration tests.
- Add stronger validation and consistent error/loading handling in frontend pages.
- Move token handling to a strategy with stronger protection against browser script access, such as an appropriately configured secure cookie architecture.
- Expand recommendations beyond already journaled movies and consider semantic or collaborative approaches if the product requirements justify them.
- Add explicit Render configuration (`render.yaml`) and document the frontend static hosting settings.
- Add pagination and query optimization for large journals, comments, and analytics datasets.

## Contributing

1. Fork or clone the repository.
2. Create a feature branch:
   ```bash
   git checkout -b feature/your-change
   ```
3. Make the change and update documentation when behavior changes.
4. Run the available checks, including `npm run lint` and manual API/frontend verification.
5. Commit the work and open a pull request with a clear description.

## License

No `LICENSE` file or other explicit license declaration was found in the repository. The project’s license is therefore currently unspecified.

## Author

The repository is owned by the GitHub account [iyersriram042006](https://github.com/iyersriram042006). No additional author biography or contact information is specified in the repository.
