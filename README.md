<div align="center">

# Deepesh Singh
AI Product Engineer — building the LLM systems users actually touch
[LinkedIn](https://www.linkedin.com/in/contactdeepesh)

</div>

I don't trust an abstraction until I've built it myself. Every system below started as a paper I didn't fully understand — I only understood it once I'd implemented it, broken it, and rebuilt it against real traffic.

### Building

**Production multi-turn chat system** — SSE streaming, context window management, prompt caching, token accounting, rate limiting, full observability stack. Handles [X concurrent users / X req/sec] at [Xms p99 latency]. Built as infrastructure, not a demo — designed for the failure modes that only show up after real users hit it.

*(Swap in your real numbers here — load-tested throughput, latency percentiles, cost-per-request reduction, uptime. This one line does more for you than the rest of the page combined.)*

### Technical focus

- **LLM application architecture** — chat orchestration, streaming UX, multi-turn context/memory — the layer that decides whether a product feels instant or feels like a chatbot
- **Inference economics** — continuous batching, quantization, caching — reduced [inference cost / latency] by [X%] on [system]
- **Retrieval & agentic tool-use** — RAG pipelines and tool-calling systems that ground model output in real data instead of letting it guess
- **Evaluation & reliability at scale** — eval harnesses and failure-mode analysis that catch regressions before users do

### How I work

I build things myself before reaching for a library — that's how I learn what the abstraction should have done for me. I read the paper before the explainer, because the tradeoffs live in the paper, not the summary. When something breaks in production, I write down what I learned — that's where the real product lessons are, not in the parts that worked on the first try.

### Stack

Python · PyTorch · Hugging Face Transformers · FastAPI · PostgreSQL · Redis · Qdrant · LangGraph · vLLM · Docker · Kubernetes · Apache Kafka · MLflow · Weights & Biases · GitHub Actions · AWS

### Direction

Building AI-native product experiences — chat systems, agentic workflows, and the infrastructure underneath — at teams where AI ships directly to millions of users: OpenAI, Anthropic, Google, Microsoft, Perplexity, Notion, Figma, Cursor (Anysphere), and comparable product-first AI teams.
