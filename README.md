# 🔗 Shortify - URL Shortener

> A high-performance URL shortening service built to explore **system design principles**, **scalable backend architecture**, and **multi-database integration**.

---

## 🎯 Project Goals

### Primary Objectives

- **Shorten URLs**: Convert long URLs into compact, shareable short links
- **Fast Redirects**: Serve redirects with minimal latency using Redis caching
- **Clean Architecture**: Implement separation of concerns with layered service architecture

### Learning Objectives (System Design)

- 🏗️ **Distributed Systems**: Multi-database architecture (PostgreSQL + Redis + MongoDB)
- ⚡ **Caching Strategies**: Redis caching with TTL and cache invalidation
- 🔐 **Hash-based ID Generation**: Deterministic short IDs using SHA-256 + Base62 encoding
- 📊 **Database Design**: Relational vs NoSQL trade-offs
- 🚀 **Performance Optimization**: Read-heavy system optimization with cache-first approach
- 🔄 **API Design**: RESTful endpoints with proper HTTP semantics

---

## 🏛️ System Architecture

### Tech Stack

- **Framework**: FastAPI (Python 3.14)
- **Primary Database**: PostgreSQL (URL storage)
- **Cache Layer**: Redis (7-day TTL for hot URLs)
- **Analytics DB**: MongoDB (prepared for v2)
- **Async ORM**: SQLAlchemy (asyncpg driver)

### Key Design Decisions

#### 1. **Hash-Based Short IDs**

- Uses SHA-256(long_url + user_id) → Base62 encoding
- Deterministic: Same URL + user → same short ID
- 7-character length = ~3.5 trillion combinations
- Collision handling: Append timestamp if duplicate detected

#### 2. **Three-Tier Caching Strategy**

```
Request → Redis (Cache) → PostgreSQL (Source of Truth)
          ↓ miss              ↓ found
          Query DB --------→ Cache result
```

#### 3. **Database Choices**

| Database   | Purpose        | Why?                                    |
| ---------- | -------------- | --------------------------------------- |
| PostgreSQL | URL mappings   | ACID compliance, relational integrity   |
| Redis      | Hot cache      | Sub-millisecond reads, automatic expiry |
| MongoDB    | Analytics (v2) | Flexible schema for click events        |

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
│   │   ├── postgres_models.py  # SQLAlchemy models
│   │   └── mongo_models.py     # MongoDB schemas (v2)
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

### Prerequisites

- Python 3.14+
- PostgreSQL
- Redis
- MongoDB (optional for v1)

### 1. Clone & Install Dependencies

```bash
git clone
cd shortify
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

Create `.env` file:

```env
# PostgreSQL
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=shortify

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
brew services start postgresql
brew services start redis
brew services start mongodb-community

# Option 2: Docker Compose
docker-compose up -d
```

### 4. Run Application

```bash
uvicorn app.main:app --reload
```

API Docs: `http://localhost:8000/docs`

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

Response: 307 Redirect → long_url
```

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

## 🧪 System Design Concepts Explored

### 1. **Scalability Patterns**

- **Horizontal Scaling**: Stateless API servers
- **Database Sharding**: Prepared for partition by user_id or short_id prefix
- **Read Replicas**: PostgreSQL read replicas for analytics queries

### 2. **Performance Optimization**

- **Cache-Aside Pattern**: Lazy loading with TTL
- **Connection Pooling**: Async database sessions
- **Index Optimization**: Indexed short_id column for O(1) lookups

### 3. **Reliability & Consistency**

- **Cache Invalidation**: Automatic on delete, TTL-based expiry
- **Idempotency**: Same input → same short ID (deterministic hashing)
- **Error Handling**: Graceful degradation if Redis fails

### 4. **Trade-offs Made**

| Decision             | Pro                          | Con                       |
| -------------------- | ---------------------------- | ------------------------- |
| Hash-based IDs       | Deterministic, no collisions | Can't customize short IDs |
| 7-day Redis TTL      | Auto-cleanup of cold URLs    | Cache miss after expiry   |
| PostgreSQL as source | Strong consistency           | Write latency vs NoSQL    |

---

## 📊 Performance Metrics (Expected)

| Operation           | Latency | Throughput   |
| ------------------- | ------- | ------------ |
| Create short URL    | ~50ms   | 1000 req/s   |
| Redirect (cached)   | ~5ms    | 10,000 req/s |
| Redirect (uncached) | ~30ms   | 2000 req/s   |

**_Note: Metrics depend on hardware and network conditions_**

---

## 🎓 Learning Resources

- [System Design Primer](https://github.com/donnemartin/system-design-primer)
- [Designing Data-Intensive Applications](https://dataintensive.net/)
- [FastAPI Best Practices](https://fastapi.tiangolo.com/async/)
- [Redis Caching Strategies](https://redis.io/docs/manual/patterns/)

---

## 🤝 Contributing

This is a learning project. Feel free to:

- Suggest optimizations
- Report issues
- Propose new features

---

## 📝 License

MIT License - Feel free to use this for learning!

---

## 👤 Author

**Harsh Vansjaliya**  
Building scalable backend systems | Exploring system design patterns

- Portfolio: [harsh-vansjaliya.vercel.app](https://harsh-vansjaliya.vercel.app)
- GitHub: [harsh6575](https://github.com/harsh6575)
- LinkedIn: [Harsh Vansjaliya](https://www.linkedin.com/in/harsh-vansjaliya-904825226/)

---

## 🔖 Tags

`#SystemDesign` `#Backend` `#FastAPI` `#Python` `#PostgreSQL` `#Redis` `#MongoDB` `#Microservices` `#Caching` `#APIDesign`
