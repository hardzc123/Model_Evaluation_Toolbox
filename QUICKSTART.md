# Quick Start Guide

Get the lifecycle-focused Model Evaluation Toolbox running in minutes.

## Prerequisites

- Python 3.10+
- Provider API keys (OpenAI, Anthropic, Google, Cohere, ...)
- Optional (for dashboard): PostgreSQL 13+, Node.js 18+

## 1. Clone & Install

```bash
git clone <repository-url>
cd Model_Evaluation_Toolbox

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt
pip install -e .
```

## 2. Configure Credentials

```bash
cp .env.template .env
```

Populate `.env` (or `config/api_keys.json`) with the API keys you need:

```
OPENAI_API_KEY=...
ANTHROPIC_API_KEY=...
GOOGLE_API_KEY=...
COHERE_API_KEY=...
```

## 3. Run the Lifecycle

### Stage 1 — Foundational Metrics
Quick smoke test for accuracy, quality, latency, and cost.

```bash
python examples/lifecycle/stage1_foundational_metrics.py \
  --model gpt-4-turbo-2024-04-09 \
  --provider openai
```

Outputs a JSON report in `artifacts/stage1/`.

### Stage 2 — Benchmarks
Execute MMLU, HumanEval, and additional datasets.

```bash
python examples/lifecycle/stage2_task_benchmarks.py \
  --model gpt-4-turbo-2024-04-09 \
  --provider openai \
  --benchmarks mmlu humaneval
```

Outputs per-benchmark metrics in `artifacts/stage2/`.

### Stage 3 — LMArena Battles
Compare candidate vs. baseline with local judges or LMArena API.

```bash
python examples/lifecycle/stage3_lmarena_simulation.py \
  --candidate-model gpt-4-turbo-2024-04-09 \
  --candidate-provider openai \
  --baseline-model claude-3-sonnet-20240229 \
  --baseline-provider anthropic
```

Produces arena results in `artifacts/stage3/`.

> Tip: Pass `--arena-base-url` and `--arena-api-key` to forward matches to a real LMArena deployment, or provide `--judge-model` to use an AI judge.

## 4. (Optional) Launch the Dashboard

```bash
# Backend
cd dashboard/backend
uvicorn app.main:app --reload

# Frontend
cd ../frontend
npm install
npm start
```

Visit `http://localhost:3000` to visualise benchmark and arena outputs.

## 5. Next Steps

- Explore `docs/lifecycle/` for configuration details per stage.
- Customize datasets and prompts to mirror production workloads.
- Wire the pipeline (`src/lifecycle/pipeline.py`) into CI to guard model promotions.

### Compare Multiple Models

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

## Common Issues

### Issue: Database connection failed
**Solution**: Ensure PostgreSQL is running and DATABASE_URL is correct

### Issue: API key not found
**Solution**: Check that .env file exists and contains your API keys

### Issue: Module not found
**Solution**: Make sure you installed the package: `pip install -e .`

### Issue: Frontend can't connect to backend
**Solution**: Ensure backend is running on port 8000

## Getting Help

- Check the full [README.md](README.md)
- Browse [examples/](examples/) for more use cases
- Open an issue on GitHub

## What's Next?

- Read about [custom evaluators](docs/custom_evaluators.md)
- Learn about [adding new providers](docs/adding_providers.md)
- Explore the [API documentation](http://localhost:8000/docs) when backend is running
