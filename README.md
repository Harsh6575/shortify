# Shortify

A URL shortener built with FastAPI, MongoDB and Redis. I built it to work through the core decisions in a read-heavy service: how to generate short IDs, how to handle collisions, and where to put the cache.

## How it works

```
POST /shorten ──> hash URL ──> check MongoDB for short_id ──> insert ──> write to Redis
GET /{id}     ──> Redis hit? ──yes──> 301
                      │no
                      └──> MongoDB ──> write to Redis ──> 301
```

**Short IDs.** The ID is the SHA-256 of the full URL: the first 8 bytes are read as an integer, Base62-encoded, and cut to 7 characters (`app/utils/hash_generator.py`). Hashing instead of a counter means no shared sequence to coordinate, and shortening the same URL twice returns the existing ID instead of creating a duplicate.

**Collisions.** Before inserting, the service looks up the generated `short_id` (`app/services/url_service.py`):

- same `short_id`, same URL: return the existing record
- same `short_id`, different URL: a real collision, so re-hash the URL with a random UUID salt and check again

A unique index on `short_id`, created at startup, is the final guard against duplicates.

**Caching.** Redis sits in front of MongoDB, keyed by `short_id`, with a 24-hour TTL. New URLs are written to Redis on creation, since a link is usually clicked soon after it's made. Reads are cache-aside: on a miss, the URL is loaded from MongoDB and put back into Redis.

## API

Interactive docs are at `http://localhost:8000/docs` once the app is running.

**Shorten a URL**

```http
POST /api/v1/urls/shorten
Content-Type: application/json

{ "full_url": "https://example.com/some/long/path" }
```

```json
{
  "short_id": "aB3xY9k",
  "full_url": "https://example.com/some/long/path",
  "created_at": "2026-10-14T09:30:00Z",
  "short_url": "http://localhost:8000/aB3xY9k"
}
```

**Redirect**

```http
GET /{short_id}
```

Returns `301` to the full URL, or `404` if the ID doesn't exist.

## Running locally

Requires Python 3 and Docker. The defaults expect a shared dev MongoDB on `localhost:27017` (`admin`/`admin123`) and Redis on `localhost:6379` (password `dev_pass`).

1. Copy the env file. The defaults point at the global containers, with Shortify's cache in Redis database 1 so its keys don't mix with other projects':

   ```bash
   cp .env.example .env
   ```

2. Install dependencies and run the app from the repo root:

   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

Without the global infra, `docker compose -f docker-compose.dev.yaml up -d` starts a standalone MongoDB and Redis on ports 27018 and 6380. Switch to the alternate URLs in `.env.example`.

## Deploying

`docker-compose.prod.yaml` runs the app, MongoDB and Redis on a single server. Only the app's port 8000 is published, and MongoDB data lives in a named volume. Redis is cache only, so it isn't persisted.

1. Copy the prod section of `.env.example` into `.env.prod` and set real passwords and `BASE_URL`.
2. Start it:

   ```bash
   docker compose -f docker-compose.prod.yaml --env-file .env.prod up -d --build
   ```

There's no TLS yet. Put a reverse proxy such as Caddy or nginx in front of port 8000 once a domain is set up.

## Project structure

```
app/
├── main.py                 # app setup, opens and closes DB connections
├── api/v1/
│   ├── urls.py             # shorten endpoint, root-level redirect
│   └── types.py            # request/response models
├── core/
│   ├── config.py           # settings from env vars or .env
│   └── db.py               # MongoDB + Redis clients, short_id index
├── models/mongo_models.py  # URL document
├── services/url_service.py # ID generation, collision handling, caching
└── utils/hash_generator.py # SHA-256 + Base62
Dockerfile
docker-compose.prod.yaml    # app + MongoDB + Redis for a single server
docker-compose.dev.yaml     # optional standalone MongoDB + Redis for dev
.env.example
```

## Known limitations

- **301 instead of 302.** Browsers cache permanent redirects, so repeat visits never reach the server. That's good for load but means clicks can't be counted. Analytics would need a 302.
- **Check-then-insert race.** Two requests for a new URL at the same time can both pass the lookup. The unique index stops the duplicate, but the second request gets a 500 instead of the existing ID.
- **Salted IDs aren't deterministic.** If a URL hit a collision and got a salted ID, shortening it again re-hashes to the original ID, sees the mismatch, and creates another salted entry.
- **Redis is a hard dependency.** If Redis is down, both endpoints fail, even though MongoDB could serve redirects alone.
- **No tests yet.** The hash generator and the collision path are the first things to cover.
