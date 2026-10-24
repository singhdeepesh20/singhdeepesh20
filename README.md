<div align="center">

<img src="assets/hero (1).svg" width="100%" alt="Deepesh Singh, AI Product Engineer"/>

<br/>

<a href="https://www.linkedin.com/in/contactdeepesh">
  <img src="https://img.shields.io/badge/LinkedIn-Connect-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn"/>
</a>
<a href="mailto:mr.deepesh.singh00@gmail.com">
  <img src="https://img.shields.io/badge/Email-Contact-334155?style=for-the-badge&logo=gmail&logoColor=white" alt="Email"/>
</a>

</div>

---

## About

I'm an AI Product Engineer who builds LLM products end to end, from first prototype to production, with a focus on the systems that make them scale.

Models are a commodity. Fast, reliable, affordable systems around them are not. That is the layer I design: **retrieval, inference, infrastructure, delivery, and observability.**

**Currently:** building production-grade RAG and agentic systems, and going deeper on system design, AWS, and DevOps.

---

## Core Competencies

| Area | What I work on |
|:--|:--|
| **LLM Applications** | Copilots, document intelligence, conversational systems with memory and streaming |
| **Retrieval** | RAG, hybrid search (dense + BM25), reranking, vector databases |
| **Agentic AI** | Multi-agent workflows, tool calling, planning with LangGraph |
| **System Design** | Latency budgets, caching layers, queues, backpressure, multi-tenancy |
| **Infrastructure and DevOps** | AWS, Docker, Kubernetes, Terraform, CI/CD, GitOps |
| **Evaluation and Observability** | Eval datasets, tracing, monitoring, SLO-driven releases |

---

## System at a Glance

How I think about a production AI product on AWS:

**Scaling playbook**

| Challenge | Approach |
|:--|:--|
| Slow first token | Stream over SSE, semantic cache, continuous batching |
| Traffic spikes | Queue-backed workers, backpressure, autoscaling |
| GPU cost | Quantization, right-sized nodes, scale down when idle |
| Provider outages | Gateway routing, retries, fallbacks |
| Bad releases | Eval gates in CI, canary rollout, automatic rollback |

---

## Tech Stack

<p>
  <img src="https://skillicons.dev/icons?i=python,pytorch,fastapi,docker,kubernetes,aws,terraform,githubactions,redis,postgres,kafka,grafana&theme=dark" alt="Tech stack icons"/>
</p>

| Category | Tools |
|:--|:--|
| **AI** | PyTorch, Hugging Face, LangChain, LangGraph, vLLM, OpenAI API, Groq |
| **Retrieval** | FAISS, Qdrant, Chroma, BM25, hybrid search |
| **Backend** | Python, FastAPI, REST, WebSockets, JWT |
| **Infrastructure** | Docker, Kubernetes, Redis, PostgreSQL, Kafka, AWS, GitHub Actions |


---

## Engineering Principles

1. **Design for failure.** Timeouts, retries, fallbacks, and idempotency from day one.
2. **Measure before shipping.** SLOs and evals decide when a change goes out.
3. **Treat cost as a feature.** Track tokens, GPU time, and cache hit rate like latency.
4. **Ship small, roll back fast.** Canary every release and automate the exit.

---

<div align="center">

**Goal:** build AI infrastructure and products that stay fast, reliable, and affordable as they grow.

</div>
