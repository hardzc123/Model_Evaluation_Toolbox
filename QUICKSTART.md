# Quick Start Guide

Get started with the Model Evaluation Toolbox in 5 minutes!

## Prerequisites

- Python 3.10 or higher
- PostgreSQL 13 or higher
- Node.js 18+ (for dashboard)
- API keys for the models you want to evaluate

## Step 1: Clone and Setup

```bash
git clone <repository-url>
cd Model_Evaluation_Toolbox

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -e .
```

## Step 2: Configure API Keys

```bash
# Copy environment template
cp .env.template .env

# Edit .env and add your API keys
nano .env
```

Add your keys:
```bash
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...
COHERE_API_KEY=...
```

## Step 3: Setup Database

```bash
# Create PostgreSQL database
createdb model_eval_db

# Update DATABASE_URL in .env
DATABASE_URL=postgresql://username:password@localhost:5432/model_eval_db
```

## Step 4: Run Your First Evaluation

```bash
# Run a basic evaluation example
cd examples/01_basic_evaluation
python run_basic_evaluation.py
```

You should see output like:
```
Basic Model Evaluation Example
======================================================================

1. Initializing OpenAI client...
2. Creating accuracy evaluator...
3. Evaluating on 8 questions...

======================================================================
RESULTS
======================================================================

Model: gpt-3.5-turbo
Provider: openai
Duration: 5.23 seconds

Metrics:
  Exact Match Accuracy: 87.50%
  Partial Match Accuracy: 100.00%
```

## Step 5: Try Cost Analysis

```bash
cd examples/02_cost_analysis
python run_cost_analysis.py
```

This will show you cost comparisons across different models.

## Step 6: Start the Dashboard

### Backend:

```bash
cd dashboard/backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend will run at `http://localhost:8000`

### Frontend:

```bash
cd dashboard/frontend
npm install
npm start
```

Frontend will open at `http://localhost:3000`

## Step 7: View the Dashboard

Open your browser to `http://localhost:3000` and explore:

- **Dashboard**: Overview of your evaluations
- **Leaderboard**: Model rankings with sorting and filtering
- **Compare Models**: Side-by-side comparison

## Next Steps

### Run More Examples

```bash
# Quality metrics
cd examples/03_quality_metrics
python run_quality_evaluation.py

# Standard benchmarks (MMLU)
cd examples/06_standard_benchmarks
python run_mmlu_benchmark.py
```

### Customize Evaluations

Create your own evaluation script:

```python
from src.providers import get_client
from src.evaluators.performance import AccuracyEvaluator
from src.evaluators.performance.accuracy_evaluator import QAExample

# Your custom dataset
dataset = [
    QAExample(question="Your question?", correct_answer="Answer"),
    # Add more...
]

# Evaluate
client = get_client("openai")
evaluator = AccuracyEvaluator(client=client, model="gpt-4")
result = evaluator.evaluate_sync(dataset)

print(f"Accuracy: {result.metrics['accuracy']:.2%}")
```

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
