# Agentic RAG Engine: Multi-Domain Knowledge Orchestrator

An enterprise-grade, low-latency Retrieval-Augmented Generation (RAG) system. This architecture moves beyond naive vector search by implementing an intelligent intent router, semantic caching, and asynchronous parallel retrieval pipelines across multiple knowledge domains.
<img width="2746" height="1500" alt="IMG_20260626_150659" src="https://github.com/user-attachments/assets/f907103e-4109-4dca-a651-7e4a7c9860c2" />

## 🧠 System Architecture
<img width="936" height="511" alt="image" src="https://github.com/user-attachments/assets/0ec7d9a9-9f7b-4f1a-943d-37fbaf1bd21f" />

1. **Edge Security:** Inbound queries are scanned for prompt injections and token-length limits before execution.
2. **Memory Tier (ElastiCache/Redis):** An SHA-256 exact-match semantic cache intercepts redundant queries to yield 0ms LLM inference latency.
3. **Intent Router:** Evaluates prompt structural intent to route queries specifically to Machine Learning, Deep Learning, or MLOps vector indices.
4. **Parallel Retrieval (OpenSearch):** Asynchronously fans out search queries across targeted databases to drastically reduce time-to-first-token.
5. **Synthesis Engine:** Securely flattens contextual hits and streams them to a local LLM (Ollama) or AWS Bedrock for final generation.

## 🚀 Tech Stack

* **Orchestration:** Python 3.11+, FastAPI
* **Presentation:** Flask, HTML5, CSS Grid, Highlight.js
* **Vector Database:** Amazon OpenSearch Serverless (Mocked via local Docker)
* **Memory / Cache:** Amazon ElastiCache Redis (Mocked via local Docker)
* **Intelligence:** Ollama (LLaMA 3.2 local) / AWS Bedrock (Claude 3 Haiku)
* **Infrastructure:** Docker, Docker Compose, GitHub Actions, AWS ECS Fargate

## ⚙️ Quick Start (Local Development)

### 1. Prerequisites

* [Docker & Docker Compose](https://www.docker.com/)
* [Ollama](https://ollama.com/) installed locally with `llama3.2` pulled.
* Python 3.11+

### 2. Initialize the Compute Engine

Start the local LLM server so it can bind to the host network and utilize your GPU:

```bash
ollama serve
```

(Leave this terminal window open).

### 3. Boot the Docker Stack

Open a second terminal in the root directory. Spin up Flask, FastAPI, Redis, and OpenSearch in detached mode:

```bash
docker-compose -f docker/docker-compose.yml up -d
```

### 4. Ingest Knowledge Base

Before querying, extract and load your PDFs into the OpenSearch indices:

```bash
python scripts/ingest_books.py
```

### 5. Access the System

* **Chat Interface:** http://localhost:5000
* **API Documentation:** http://localhost:8000/docs
* **Database Manager:** http://localhost:8001

### 6. Clean Teardown

```bash
docker-compose -f docker/docker-compose.yml down
```
