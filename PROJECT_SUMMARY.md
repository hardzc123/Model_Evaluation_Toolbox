# Project Summary: AI Model Evaluation Toolbox

## 1. Overview

The repository now presents the AI model evaluation journey as a **three-stage lifecycle**:

1. **Foundational metrics** to validate correctness, safety, latency, and cost.
2. **Task & domain benchmarks** to earn confidence on established datasets.
3. **Arena mode (LMArena)** to capture pairwise preferences and qualitative nuance.

Lifecycle orchestration lives under `src/lifecycle/` with companion docs in `docs/lifecycle/`.

## 2. Lifecycle Highlights

### Stage 1 – Foundational Metrics
- `FoundationalEvaluationSuite` aggregates accuracy/F1, BLEU/ROUGE/BERTScore, latency, and cost checks.
- Smoke-test datasets shipped in `examples/lifecycle/stage1_foundational_metrics.py`.
- Results persist to `artifacts/stage1` for dashboard ingestion or CI gating.

### Stage 2 – Task & Domain Benchmarks
- `BenchmarkEvaluationSuite` wraps MMLU, HumanEval, and forthcoming benchmarks.
- Configurable via `BenchmarkRunConfig` for subject selection and sample counts.
- Example runner (`examples/lifecycle/stage2_task_benchmarks.py`) demonstrates multi-benchmark execution.

### Stage 3 – Arena Evaluations (LMArena)
- `LMArenaEvaluator` supports real API submissions (via `LMArenaClient`) or local judge fallbacks.
- `ArenaEvaluationSuite` coordinates candidate vs. baseline tournaments with optional judge models.
- Example script `examples/lifecycle/stage3_lmarena_simulation.py` generates head-to-head reports.

## 3. Additional Capabilities

- **Multi-Provider Clients**: OpenAI, Anthropic, Google, Cohere. Extensible via `src/providers/factory.py`.
- **Dashboard**: FastAPI + React app with leaderboards, filters, and cost efficiency views.
- **Cost Analysis**: `CostAnalyzer` leverages `config/models_registry.json` for price modeling.
- **Token Utilities**: Shared token counting and retry helpers under `src/utils/`.
- **Testing & Quality**: pytest, pytest-asyncio, Ruff, Black, and mypy integrations.

## 4. Project Structure

```
Model_Evaluation_Toolbox/
├── config/                          # Model registry & API key templates
├── docs/
│   └── lifecycle/                   # Lifecycle overview + stage briefs
├── examples/
│   └── lifecycle/                   # Stage-aligned runnable scripts
├── src/
│   ├── lifecycle/                   # Orchestrators and pipeline
│   ├── evaluators/                  # Metric suites (performance/cost/quality/speed/arena)
│   ├── benchmarks/                  # MMLU, HumanEval, etc.
│   ├── providers/                   # API clients
│   └── utils/                       # Logging, token counting, retry, ...
├── dashboard/                       # FastAPI backend + React frontend
├── tests/                           # Unit & integration tests
└── artifacts/                       # Generated reports (created at runtime)
```

## 5. Quick Start for Maintainers

### Environment
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

### API Keys
```bash
cp .env.template .env
```
Populate provider keys and optional database URL.

### Lifecycle Commands
```bash
# Stage 1
python examples/lifecycle/stage1_foundational_metrics.py \
  --model gpt-4-turbo-2024-04-09 --provider openai

# Stage 2
python examples/lifecycle/stage2_task_benchmarks.py \
  --model gpt-4-turbo-2024-04-09 --provider openai --benchmarks mmlu humaneval

# Stage 3 (local simulation or real LMArena via --arena-base-url)
python examples/lifecycle/stage3_lmarena_simulation.py \
  --candidate-model gpt-4-turbo-2024-04-09 --baseline-model claude-3-sonnet-20240229
```

### Dashboard
```bash
cd dashboard/backend && uvicorn app.main:app --reload
cd dashboard/frontend && npm start
```
Visit `http://localhost:3000`.

## 6. Roadmap Ideas

- Expand Stage 2 with GSM8K, TruthfulQA, and custom enterprise datasets.
- Add automated promotion criteria (e.g., minimum Stage 1 thresholds before Stage 2).
- Integrate continuous evaluation jobs with GitHub Actions and dashboard webhooks.
- Support multi-judge ensembles (human + AI) in Stage 3.

## 7. References

- `README.md` – lifecycle overview and quick commands.
- `docs/lifecycle/*` – deep dives into each stage.
- `QUICKSTART.md` – concise installation + first run steps.
- `config/models_registry.json` – pricing and model metadata used across stages.

The repository is now aligned around the lifecycle narrative, making it easier to communicate evaluation coverage and extend each stage independently.

### 🎯 Leaderboard with Sorting
- Sort by accuracy, latency, cost, quality, efficiency
- Filter by provider
- Real-time updates
- Click column headers to sort

### 💰 Cost Analysis
- Per-request cost calculation
- Monthly cost estimates
- Cost efficiency rankings (quality per dollar)
- Compare costs across all models

### ⚡ Speed Benchmarks
- Mean, median, P95, P99 latencies
- Throughput (requests/second)
- Tokens per second
- Concurrent request testing

### 📊 Quality Metrics
- BLEU scores for text generation
- ROUGE-1, ROUGE-2, ROUGE-L
- BERTScore for semantic similarity
- Custom metric support

### 🏆 Standard Benchmarks
- MMLU: 57 subjects across knowledge domains
- HumanEval: Code generation and execution
- Easy to add more benchmarks

## Configuration

### Models Registry

Edit `config/models_registry.json` to:
- Add new models
- Update pricing
- Modify capabilities
- Set default models for benchmarks

### API Keys

Three options:
1. **.env file** (recommended for local dev)
2. **config/api_keys.json** (for structured config)
3. **Environment variables** (for production)

## Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=src --cov-report=html

# Specific tests
pytest tests/unit/test_config.py
```

## Development

```bash
# Install pre-commit hooks
pre-commit install

# Format code
black src/
ruff check src/ --fix

# Type checking
mypy src/ --ignore-missing-imports
```

## API Documentation

When backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Common Use Cases

### 1. Compare Model Costs

```python
from src.evaluators.cost import CostAnalyzer

analyzer = CostAnalyzer()
comparison = analyzer.compare_models(
    model_ids=["gpt-4", "claude-3-opus-20240229", "gemini-1.5-pro"],
    input_tokens=1000,
    output_tokens=500,
    requests_per_day=1000
)
print(comparison)
```

### 2. Benchmark Model Speed

```python
from src.providers import get_client
from src.evaluators.speed import LatencyBenchmark

client = get_client("openai")
benchmark = LatencyBenchmark(client=client, model="gpt-3.5-turbo")
result = await benchmark.evaluate(num_requests=100)
print(f"Mean latency: {result.metrics['mean_latency_ms']:.2f}ms")
```

### 3. Evaluate Quality

```python
from src.evaluators.quality import TextQualityEvaluator
from src.evaluators.quality.text_quality_evaluator import TextPair

dataset = [
    TextPair(
        prompt="Summarize: [text]",
        reference="Expected summary"
    )
]

evaluator = TextQualityEvaluator(client=client, model="gpt-4")
result = await evaluator.evaluate(dataset)
print(f"BLEU: {result.metrics['mean_bleu']:.3f}")
```

### 4. Find Best Value Model

```python
analyzer = CostAnalyzer()
quality_scores = {
    "gpt-4": 0.92,
    "claude-3-opus-20240229": 0.94,
    "gemini-1.5-pro": 0.90
}

best_value = analyzer.find_best_value(
    model_ids=list(quality_scores.keys()),
    quality_scores=quality_scores,
    input_tokens=1000,
    output_tokens=500
)
print(best_value)
```

## What's NOT Included (Future Work)

- Real-time streaming evaluation
- Multi-modal evaluation (images, audio, video)
- Custom benchmark builder UI
- Automated report generation
- Model fine-tuning evaluation
- A/B testing framework
- User authentication in dashboard
- Deployment scripts (Docker, Kubernetes)

## File Statistics

- **Total Files**: 70+
- **Lines of Code**: ~6,800+
- **Python Modules**: 30+
- **React Components**: 4
- **Example Scripts**: 5
- **Test Files**: 3
- **Documentation**: 5 comprehensive guides

## Technologies Used

### Backend
- Python 3.10+
- FastAPI
- SQLAlchemy
- PostgreSQL
- Pydantic
- Asyncio
- OpenAI SDK
- Anthropic SDK
- Google Generative AI SDK
- Cohere SDK

### Frontend
- React 18
- TypeScript
- Tailwind CSS
- Axios
- React Router

### Development
- Pytest
- Black
- Ruff
- MyPy
- Pre-commit
- GitHub Actions

## Next Steps for You

1. **Add your API keys** to `.env`
2. **Set up PostgreSQL** database
3. **Run examples** to test functionality
4. **Start dashboard** to visualize results
5. **Run your own evaluations** on models you care about
6. **Customize** as needed for your use case

## Support

- 📖 Check [README.md](README.md) for detailed info
- 🚀 See [QUICKSTART.md](QUICKSTART.md) for setup
- 🤝 Read [CONTRIBUTING.md](CONTRIBUTING.md) to contribute
- 💬 Open issues on GitHub for help

## License

MIT License - See [LICENSE](LICENSE) file

---

**Built with best practices in software engineering for AI model evaluation.**
