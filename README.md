# Message API - Platform Engineering & SRE Assessment

A production-ready REST API for managing short text messages. This project is intentionally focused to serve as a showcase for **Site Reliability Engineering (SRE) and DevOps excellence**, prioritizing operational readiness over complex business logic.

It demonstrates production-grade observability, comprehensive testability, CI/CD automation, and thread-safe data handling.

## 🎯 Key Metrics & Highlights
- **41 Automated Tests**: Running with a 100% passing rate.
- **6 REST Endpoints**: Handling standard CRUD operations and system health.
- **5 Validation Rules**: Strict business logic enforcement (Fail-fast architecture).
- **7 Observability Metrics**: Prometheus-ready metrics tracking throughput, response codes, and errors.

---

## ⚙️ Prerequisites
Before running the application, ensure you have the following installed to guarantee a frictionless Developer Experience (DX):
- **Docker & Docker Compose** (Required for the standard deployment path)
- **Make** (For executing automation shortcuts)
- *Optional:* `curl` (For testing endpoints locally)

---

## 🚀 Quick Start (The Golden Path)

The local development stack perfectly mirrors production using Docker Compose.

**1. Start the infrastructure:**

```bash
make docker-compose-up
```

(Alternatively):

```bash
docker compose up -d
```

2. Verify the health endpoint:

```bash
curl http://localhost:8000/health
```

(Expected: {"status": "healthy", ...}).

3. Run the test suite:

```bash
make docker-test
```

(Expected: ... 41 passed in 2.04s ✅).

4. View Prometheus-ready metrics:

```bash
curl http://localhost:8000/metrics | head
```

(Expected: JSON output showing total_requests, successful_requests, etc.).

5. Clean up:

```bash
make docker-compose-down
```


🏗️ Project Architecture & Components

This project follows a clear, layered architecture to keep concerns separated and tests focused. Below is a concise overview of each layer and the key files you’ll interact with.

**Application Layer (`app/`)**
- `app/main.py`: HTTP entrypoint — exposes the 6 REST endpoints and wires routes.
- `app/models.py`: Pydantic models and request/response schemas.
- `app/validators.py`: Business-rule validators (fail-fast behavior; 5 rules).
- `app/storage.py`: Thread-safe in-memory storage (uses `threading.Lock`).
- `app/metrics.py`: Prometheus instrumentation and metric definitions.
- `app/config.py`: Environment and configuration helpers (12-factor friendly).

**Testing Layer (`tests/`)**
- `tests/test_api.py`: End-to-end tests for API behavior.
- `tests/test_validators.py`: Unit tests for validation logic.
- `tests/test_storage.py`: Concurrency and storage correctness tests.

> Note: There are 41 tests in total, covering API, validators and storage behavior.

**Infrastructure & Automation**
- `Dockerfile`: Multi-stage build using a non-root user for production images.
- `.github/workflows/ci-cd.yml`: CI pipeline (test → lint → build → scan → push).
- `Makefile`: Convenience targets (start, test, lint, clean, etc.).
- `docker-compose.yml`: Local development stack mirroring production.
- `prometheus.yml`: Example Prometheus scrape configuration for the `/metrics` endpoint.

Design principles: Observability (Prometheus-ready `/metrics`), Automation (CI & Make targets), Defense-in-depth (Pydantic → validators → thread-safe storage), and Pragmatism (Docker-first, easy to lift to Kubernetes).

🛡️ SRE Mindset

The SRE mindset guides the design and operational choices in this project. Key principles applied:

- **Observability:** Prometheus metrics exposed at `/metrics`, providing clear measurements of traffic and responses to accelerate troubleshooting.
- **Automation:** Automated CI (test → lint → build → scan) and `Make` targets reduce human error and speed recovery.
- **Layered resilience:** Schema validation with Pydantic → business validators → thread-safe storage.
- **Secure by default:** Multi-stage Docker image and non-root runtime enforced in the `Dockerfile`.
- **Operational pragmatism:** A local `docker-compose.yml` mirrors production, easing migration to Kubernetes or an external database when needed.

These principles keep the service observable, secure, and easy to operate in real environments.
