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
The application is structured into three distinct layers, prioritizing the Separation of Concerns to ensure everything is testable, isolated, and easy to debug.

1. Application Layer (app/)
main.py: The entry point. Exposes 6 REST endpoints.

models.py: Handles Pydantic validation to ensure type safety.

validators.py: Enforces 5 strict business rules before any data is processed.

storage.py: In-memory storage utilizing threading.Lock() to ensure thread-safety and prevent race conditions.

metrics.py: Tracks 7 distinct operational metrics for observability.

config.py: Manages environment variables for 12-factor app compliance.

2. Testing Layer (tests/)
Contains 41 unit tests broken down into API tests, validator tests, and storage tests.

SRE Principle: 100% passing tests provide the confidence required for automated, risk-free deployments.

3. Infrastructure & Automation Layer
Dockerfile: A multi-stage build utilizing a non-root user to ensure a secure, production-ready image.

.github/workflows/ci-cd.yml: A 5-stage automated pipeline (test → lint → build → scan → push).

Makefile: Contains 20 automation commands to eliminate human error (toil) during operations.

prometheus.yml: Configuration for metrics collection.

🛡️ The SRE Mindset: Why it's built this way
This repository relies on several core Platform Engineering principles:

Observability is Everything: The /metrics endpoint is ready for Prometheus scraping. You cannot operate what you cannot see.

Automation Eliminates Human Error: The GitHub Actions pipeline ensures that code is tested, linted, and scanned for vulnerabilities before it is ever built or pushed.

Defense in Depth: Data passes through Pydantic type-checking, then custom business validators, and finally a thread-safe storage lock.

Pragmatism: We start simple with Docker as the deployment unit. If the scale demands it, the stateless design allows us to easily transition to Kubernetes or an external database like PostgreSQL.
