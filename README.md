# 🎯 AI Model Evaluation Toolbox

End-to-end tooling for the **complete evaluation lifecycle** of AI language models — from foundational precision/recall checks to academic benchmarks and LMArena head-to-head battles.

## 🔄 Lifecycle Overview

| Stage | Question Answered | Delivered By |
| ----- | ----------------- | ------------ |
| **Stage 1 – Foundational Metrics** | Is the model ready to leave the lab? | Accuracy, precision/recall, cost, latency, safety smoke tests. |
| **Stage 2 – Task & Domain Benchmarks** | How does it stack up on established standards? | MMLU, HumanEval, GSM8K, and other curated datasets. |
| **Stage 3 – Arena Evaluations (LMArena)** | Which model wins in real conversations? | Pairwise battles, judge workflows, rolling leaderboards. |

Navigate the lifecycle with the new orchestration layer under `src/lifecycle/` and companion docs in `docs/lifecycle/`.

## 🧭 Lifecycle Stage Details

- **Stage 1 – Foundational Metrics**: `FoundationalEvaluationSuite` aggregates accuracy/F1, BLEU/ROUGE/BERTScore, latency sampling, and cost modelling so you can gate models before deeper testing. Outputs land in `artifacts/stage1/` for CI or dashboard ingestion.
- **Stage 2 – Task & Domain Benchmarks**: `BenchmarkEvaluationSuite` wraps MMLU, HumanEval, and additional datasets. Configure samples, subjects, and ordering with `BenchmarkRunConfig`; results populate `artifacts/stage2/`.
- **Stage 3 – Arena Evaluations**: `ArenaEvaluationSuite` drives LMArena-style tournaments with API-backed or local judges, producing head-to-head statistics and match metadata under `artifacts/stage3/`.

## ✨ What's Inside

- **Lifecycle Orchestration**: `FoundationalEvaluationSuite`, `BenchmarkEvaluationSuite`, `ArenaEvaluationSuite`, and `EvaluationLifecyclePipeline`.
- **Multi-Provider API Clients**: OpenAI, Anthropic, Google (Gemini), Cohere, and more.
- **Metric Suites**: Accuracy/F1, BLEU/ROUGE/BERTScore, latency, token-cost analytics, safety hooks.
- **Benchmark Integrations**: MMLU, HumanEval, with scaffolding for more datasets.
- **Arena Mode**: LMArena client, local judge fallbacks, and example playlists for modern “battle” style evaluations.
- **Dashboard**: FastAPI + React app for leaderboard visualisation and cost/performance tracking.

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- PostgreSQL 13+ (dashboard backend)
- Node.js 18+ (dashboard frontend)
- Provider API keys (configure via `.env` or `config/api_keys.json`)

### Installation

```bash
git clone https://github.com/yourusername/Model_Evaluation_Toolbox.git
cd Model_Evaluation_Toolbox
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
```

Copy the environment template and fill in keys:

```bash
cp .env.template .env
```

(Optional) Prepare PostgreSQL and dashboard:

```bash
createdb model_eval_db
cd dashboard/backend && alembic upgrade head
cd ../frontend && npm install
```

## 🛠 Running the Lifecycle Stages

| Stage | Command | Output |
| ----- | ------- | ------ |
| Stage 1 | `python examples/lifecycle/stage1_foundational_metrics.py --model gpt-4-turbo-2024-04-09 --provider openai` | `artifacts/stage1/<model>_stage1.json` |
| Stage 2 | `python examples/lifecycle/stage2_task_benchmarks.py --model gpt-4-turbo-2024-04-09 --provider openai --benchmarks mmlu humaneval` | `artifacts/stage2/<model>_stage2.json` |
| Stage 3 | `python examples/lifecycle/stage3_lmarena_simulation.py --candidate-model gpt-4-turbo-2024-04-09 --baseline-model claude-3-sonnet-20240229` | `artifacts/stage3/<candidate>_vs_<baseline>_stage3.json` |

The pipeline module (`src/lifecycle/pipeline.py`) stitches stages together if you want a single orchestrated run.

> 💡 **Tip**: For Stage 3 you can forward matches to a real LMArena deployment with `--arena-base-url` and `--arena-api-key`, or provide `--judge-model/--judge-provider` to use an internal judge model.

## 🏗 Capabilities & Engineering Practices

- Multi-provider architecture with async clients, retry logic, rate limiting, and token accounting.
- Metric coverage across performance, quality, safety readiness, latency, and cost.
- FastAPI + PostgreSQL backend with React/Tailwind dashboard for leaderboards and visualisations.
- Extensive evaluator library: classification QA, text quality (BLEU/ROUGE/BERTScore), cost analytics, latency benchmarking, and arena judging.
- Type hints, Pydantic validation, structured logging, and configurability via `.env` + JSON registries.
- Testing toolchain: pytest, pytest-asyncio, coverage reporting, Ruff, Black, and mypy.

## 📚 Documentation Map

- `docs/lifecycle/overview.md` – lifecycle map.
- `docs/lifecycle/stage1_foundational_metrics.md` – precision/recall, latency, cost guardrails.
- `docs/lifecycle/stage2_task_benchmarks.md` – configuring benchmark suites.
- `docs/lifecycle/stage3_arena_evaluations.md` – LMArena setup, judge strategies, simulators.
- Existing guides under `docs/` remain available for providers, API usage, and dashboard operations.

## 📂 Project Structure

```
Model_Evaluation_Toolbox/
├── config/                      # Model registry and API key templates
├── docs/
│   └── lifecycle/               # Stage-by-stage lifecycle guides
├── examples/
│   └── lifecycle/               # Stage-specific runnable scripts
├── src/
│   ├── lifecycle/               # Orchestration layer for all stages
│   ├── evaluators/              # Metric suites (performance, cost, speed, quality, arena)
│   ├── benchmarks/              # MMLU, HumanEval, and scaffold for more datasets
│   ├── providers/               # API clients (OpenAI, Anthropic, Google, Cohere, ...)
│   └── utils/                   # Logging, token counting, retry helpers
├── dashboard/                   # FastAPI backend + React frontend
├── tests/                       # Unit and integration tests
└── artifacts/                   # Generated reports (created at runtime)
```

## 🎨 Dashboard

- FastAPI backend (`dashboard/backend`) with PostgreSQL storage.
- React + Tailwind frontend (`dashboard/frontend`) for leaderboards, filtering, and visual dashboards.
- Export benchmark + arena results as CSV/JSON for analytics workflows.

## 🧪 Testing

```bash
pytest
pytest --cov=src --cov-report=html
```

Use `pytest tests/unit/` or `pytest tests/integration/` for targeted suites.

## 🤝 Contributing

1. Fork the repository.
2. Create a branch (`git checkout -b feature/lifecycle-updates`).
3. Make your changes and add tests where relevant.
4. Run formatting (`ruff`, `black`) and tests.
5. Open a pull request.

## 🗺 Roadmap Ideas

- Expand Stage 2 with GSM8K, TruthfulQA, and enterprise-specific datasets.
- Automate promotion criteria (e.g., minimum Stage 1 thresholds before Stage 2).
- Integrate scheduled evaluations via CI/CD and surface results directly in the dashboard.
- Support multi-judge ensembles that blend human feedback with model judges.

## 📄 License

MIT License — see [LICENSE](LICENSE).

## 📘 Maintainer Reference Map

- Lifecycle documentation: `docs/lifecycle/`
- Provider configuration: `config/api_keys.template.json`, `config/models_registry.json`
- Orchestration entrypoint: `src/lifecycle/pipeline.py`
- Dashboard backend: `dashboard/backend`, frontend: `dashboard/frontend`

## 📞 Support

- Issues: [GitHub Issues](https://github.com/yourusername/Model_Evaluation_Toolbox/issues)
- Email: support@example.com
- Community: Discord (link TBD)

---

Made with ❤️ by the AI Evaluation Community.
