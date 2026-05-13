# 🔗 Shortify - URL Shortener

> A high-performance URL shortening service I built to explore **system design principles**, **scalable backend architecture**, and **multi-database integration**.

Hi! I'm **Harsh Vansjaliya**, a Software Developer passionate about Backend Systems and System Design. You can find more of my work on my [Portfolio](https://harsh-vansjaliya.vercel.app), check out my code on [GitHub](https://github.com/harsh6575), or connect with me on [LinkedIn](https://www.linkedin.com/in/harsh-vansjaliya-904825226/).

---

## 🎯 My Project Goals

### Primary Objectives

- **Shorten URLs**: I wanted to convert long URLs into compact, shareable short links.
- **Fast Redirects**: My goal was to serve redirects with minimal latency using Redis caching.
- **Clean Architecture**: I focused on implementing separation of concerns with a layered service architecture.

### Learning Objectives (System Design)

- 🏗️ **Distributed Systems**: I built a multi-database architecture (MongoDB + Redis).
- ⚡ **Caching Strategies**: I implemented Redis caching with TTL and cache invalidation.
- 🔐 **Hash-based ID Generation**: I used deterministic short IDs using SHA-256 + Base62 encoding.
- 🚀 **Performance Optimization**: I optimized a read-heavy system with a cache-first approach.
- 🔄 **API Design**: I designed RESTful endpoints with proper HTTP semantics.

---

## 🏛️ System Architecture

### Tech Stack

- **Framework**: FastAPI (Python 3.14)
- **Primary Database**: MongoDB (URL storage & Analytics)
- **Cache Layer**: Redis (7-day TTL for hot URLs)
- **Async Driver**: Motor (Async MongoDB driver)

### Key Design Decisions I Made

#### 1. **Hash-Based Short IDs**

- I used `SHA-256(long_url + user_id) → Base62 encoding`.
- I made it deterministic: the same URL + user results in the same short ID.
- The 7-character length gives me ~3.5 trillion combinations.
- For collision handling, I append a unique salt (UUID) and re-hash if a duplicate is detected.

#### 2. **Three-Tier Caching Strategy**

```
Request → Redis (Cache) → MongoDB (Source of Truth)
          ↓ miss              ↓ found
          Query DB --------→ Cache result
```

#### 3. **Database Choices**

| Database | Purpose        | Why I Chose It                          |
| -------- | -------------- | --------------------------------------- |
| MongoDB  | URL mappings   | Flexible schema, fast writes            |
| Redis    | Hot cache      | Sub-millisecond reads, automatic expiry |

---

## 📂 Project Structure

```
shortify/
├── app/
│   ├── main.py                 # FastAPI app with lifespan management
│   ├── api/
│   │   ├── routes.py           # API endpoints
│   │   └── schemas.py          # Pydantic models
│   ├── core/
│   │   ├── config.py           # Environment configuration
│   │   └── db.py               # Database connections & session management
│   ├── models/
│   │   └── mongo_models.py     # MongoDB schemas
│   ├── services/
│   │   └── url_service.py      # Business logic layer
│   ├── utils/
│   │   ├── hash_generator.py   # SHA-256 + Base62 implementation
│   │   └── redis_cache.py      # Cache operations
│   └── tests/                  # Unit & integration tests
├── requirements.txt
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 🚀 Features

### ✅ Version 1 (Current)

- [x] Create short URLs with hash-based IDs
- [x] Instant redirects with Redis caching
- [x] Delete short URLs
- [x] View recent URLs (dev endpoint)
- [x] Automatic cache refresh on access (TTL reset)
- [x] Collision detection and handling

### 🔮 Version 2 (Planned)

- [ ] Click analytics (MongoDB integration)
- [ ] Custom short IDs (user-defined aliases)
- [ ] URL expiration dates
- [ ] Rate limiting (per-user quotas)
- [ ] QR code generation
- [ ] Analytics dashboard

---

## 🛠️ Setup & Installation

Here is how you can set up my project locally:

### Prerequisites

- Python 3.14+
- MongoDB
- Redis

### 1. Clone & Install Dependencies

```bash
git clone https://github.com/harsh6575/shortify.git
cd shortify
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file:

```env
# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# MongoDB
MONGO_URL=mongodb://localhost:27017
MONGO_DB=shortify
```

### 3. Start Services

```bash
# Option 1: Local services
brew services start redis
brew services start mongodb-community

# Option 2: Docker Compose
docker-compose up -d
```

### 4. Run Application

```bash
uvicorn app.main:app --reload
```

API Docs will be available at: `http://localhost:8000/docs`

---

## 📡 API Endpoints

### Create Short URL

```bash
POST /api/shorten
Content-Type: application/json

{
  "long_url": "https://example.com/very/long/url",
  "user_id": 123
}

Response:
{
  "short_id": "aBc1234",
  "long_url": "https://example.com/very/long/url",
  "created_at": "2025-11-09T10:30:00",
  "short_url": "http://localhost:8000/aBc1234"
}
```

### Redirect to Long URL

```bash
GET /{short_id}

Response: 301 Redirect → long_url
```
*(Note: Swagger UI will accurately reflect the 301 redirect response thanks to my recent codebase improvements!)*

### Delete Short URL

```bash
DELETE /api/urls/{short_id}

Response:
{
  "message": "Short URL 'aBc1234' deleted successfully"
}
```

### Get Recent URLs (Dev)

```bash
GET /api/urls/recent?limit=10

Response:
{
  "urls": [...],
  "total": 10
}
```

---

## 🧪 System Design Concepts I Explored

### 1. **Scalability Patterns**

- **Horizontal Scaling**: I designed stateless API servers.
- **Database Sharding**: I prepared the architecture for partitioning by `user_id` or `short_id` prefix.
- **Read Replicas**: I planned for MongoDB read replicas for analytics queries.

### 2. **Performance Optimization**

- **Cache-Aside Pattern**: I used lazy loading with a TTL.
- **Connection Pooling**: I implemented async database sessions.
- **Index Optimization**: I indexed the `short_id` column for O(1) lookups.

### 3. **Reliability & Consistency**

- **Cache Invalidation**: Automatically clears cache on delete, with TTL-based expiry as a fallback.
- **Idempotency**: Same input always results in the same short ID (deterministic hashing).
- **Error Handling**: Graceful degradation if Redis fails.

### 4. **Trade-offs I Made**

| Decision          | Pro                          | Con                       |
| ----------------- | ---------------------------- | ------------------------- |
| Hash-based IDs    | Deterministic, no collisions | Can't customize short IDs |
| 7-day Redis TTL   | Auto-cleanup of cold URLs    | Cache miss after expiry   |
| MongoDB as source | Flexible schema, fast writes | Eventual consistency      |

---

## 📊 Performance Metrics (Expected)

| Operation           | Latency | Throughput   |
| ------------------- | ------- | ------------ |
| Create short URL    | ~50ms   | 1000 req/s   |
| Redirect (cached)   | ~5ms    | 10,000 req/s |
| Redirect (uncached) | ~30ms   | 2000 req/s   |

**_Note: Metrics depend on hardware and network conditions._**

---

## 🎓 Learning Resources I Found Helpful

- [System Design Primer](https://github.com/donnemartin/system-design-primer)
- [Designing Data-Intensive Applications](https://dataintensive.net/)
- [FastAPI Best Practices](https://fastapi.tiangolo.com/async/)
- [Redis Caching Strategies](https://redis.io/docs/manual/patterns/)

---

## 🤝 Contributing

This is my personal learning project, and I would love your feedback! Feel free to:

- Suggest optimizations
- Report issues
- Propose new features

---

## 📝 License

MIT License - Feel free to use this for learning!

---

## 👤 About Me

**Harsh Vansjaliya**  
Software Developer | Exploring Backend & System Design

- 🌐 **Portfolio:** [harsh-vansjaliya.vercel.app](https://harsh-vansjaliya.vercel.app)
- 💻 **GitHub:** [harsh6575](https://github.com/harsh6575)
- 🔗 **LinkedIn:** [Harsh Vansjaliya](https://www.linkedin.com/in/harsh-vansjaliya-904825226/)

---

## 🔖 Tags

`#SystemDesign` `#Backend` `#FastAPI` `#Python` `#Redis` `#MongoDB` `#Microservices` `#Caching` `#APIDesign`
