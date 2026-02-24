# Message API - Platform Engineering & SRE Assessment

A production-ready REST API for managing short text messages. [cite_start]This project is intentionally focused to serve as a showcase for **Site Reliability Engineering (SRE) and DevOps excellence**, prioritizing operational readiness over complex business logic[cite: 78, 80].

It demonstrates production-grade observability, comprehensive testability, CI/CD automation, and thread-safe data handling.

## 🎯 Key Metrics & Highlights
* [cite_start]**41 Automated Tests**: Running with a 100% passing rate[cite: 96, 127].
* [cite_start]**6 REST Endpoints**: Handling standard CRUD operations and system health[cite: 95, 126].
* [cite_start]**5 Validation Rules**: Strict business logic enforcement (Fail-fast architecture)[cite: 126].
* [cite_start]**7 Observability Metrics**: Prometheus-ready metrics tracking throughput, response codes, and errors[cite: 126].

---

## ⚙️ Prerequisites
Before running the application, ensure you have the following installed to guarantee a frictionless Developer Experience (DX):
* **Docker & Docker Compose** (Required for the standard deployment path)
* **Make** (For executing automation shortcuts)
* *Optional:* `curl` (For testing endpoints locally)

---

## 🚀 Quick Start (The Golden Path)

The local development stack perfectly mirrors production using Docker Compose.

**1. Start the infrastructure:**
`make docker-compose-up` or `docker compose up -d`
*(This spins up the API on `localhost:8000`).*

**2. Verify the health endpoint:**
`curl http://localhost:8000/health`
*(Expected: `{"status": "healthy", ...}`).*

**3. Run the test suite:**
`make test`
*(Expected: `... 41 passed in 2.04s ✅`).*

**4. View Prometheus-ready metrics:**
`curl http://localhost:8000/metrics | head`
[cite_start]*(Expected: JSON output showing `total_requests`, `successful_requests`, etc.)[cite: 98, 99].*

**5. Clean up:**
`make docker-compose-down` or `docker compose down`

---

## 🏗️ Project Architecture & Components

[cite_start]The application is structured into three distinct layers, prioritizing the **Separation of Concerns** to ensure everything is testable, isolated, and easy to debug[cite: 95, 96].

### 1. Application Layer (`app/`)
* **`main.py`**: The entry point. [cite_start]Exposes 6 REST endpoints[cite: 125, 126].
* [cite_start]**`models.py`**: Handles Pydantic validation to ensure type safety[cite: 126].
* [cite_start]**`validators.py`**: Enforces 5 strict business rules before any data is processed[cite: 126].
* [cite_start]**`storage.py`**: In-memory storage utilizing `threading.Lock()` to ensure thread-safety and prevent race conditions[cite: 126].
* [cite_start]**`metrics.py`**: Tracks 7 distinct operational metrics for observability[cite: 126].
* [cite_start]**`config.py`**: Manages environment variables for 12-factor app compliance[cite: 126].

### 2. Testing Layer (`tests/`)
* [cite_start]Contains 41 unit tests broken down into API tests, validator tests, and storage tests[cite: 126, 127].
* [cite_start]**SRE Principle:** 100% passing tests provide the confidence required for automated, risk-free deployments[cite: 96, 97].

### 3. Infrastructure & Automation Layer
* [cite_start]**`Dockerfile`**: A multi-stage build utilizing a non-root user to ensure a secure, production-ready image[cite: 96].
* [cite_start]**`.github/workflows/ci-cd.yml`**: A 5-stage automated pipeline (`test` → `lint` → `build` → `scan` → `push`)[cite: 127].
* [cite_start]**`Makefile`**: Contains 20 automation commands to eliminate human error (toil) during operations[cite: 127].
* [cite_start]**`prometheus.yml`**: Configuration for metrics collection[cite: 127].

---

## 🛡️ The SRE Mindset: Why it's built this way

This repository relies on several core Platform Engineering principles:
1. [cite_start]**Observability is Everything:** The `/metrics` endpoint is ready for Prometheus scraping[cite: 96, 97]. You cannot operate what you cannot see.
2. [cite_start]**Automation Eliminates Human Error:** The GitHub Actions pipeline ensures that code is tested, linted, and scanned for vulnerabilities before it is ever built or pushed[cite: 97].
3. [cite_start]**Defense in Depth:** Data passes through Pydantic type-checking, then custom business validators, and finally a thread-safe storage lock[cite: 97]. 
4. [cite_start]**Pragmatism:** We start simple with Docker as the deployment unit[cite: 97]. [cite_start]If the scale demands it, the stateless design allows us to easily transition to Kubernetes [cite: 104] [cite_start]or an external database like PostgreSQL[cite: 101].