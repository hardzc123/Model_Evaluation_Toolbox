# Project Summary: AI Model Evaluation Toolbox

## Overview

A comprehensive, production-ready toolkit for evaluating and benchmarking AI language models across multiple providers with an interactive dashboard.

## What Has Been Implemented

### ✅ Complete Feature Set

#### 1. Core Evaluation Framework
- **Performance Metrics**: Accuracy, precision, recall, F1 score
- **Cost Analysis**: Token counting, pricing calculation, cost efficiency
- **Speed Benchmarks**: Latency, throughput, tokens per second
- **Quality Metrics**: BLEU, ROUGE, BERTScore
- **Safety Evaluation**: Framework ready for toxicity and bias testing

#### 2. Multi-Provider Support
- ✅ OpenAI (GPT-4, GPT-3.5, etc.)
- ✅ Anthropic (Claude 3 family)
- ✅ Google (Gemini 1.5 Pro/Flash)
- ✅ Cohere (Command R+)
- 🔧 Extensible architecture for adding more providers

#### 3. Standard Benchmarks
- ✅ MMLU (Massive Multitask Language Understanding)
- ✅ HumanEval (Code generation)
- 🔧 Framework ready for additional benchmarks

#### 4. Professional Dashboard
- ✅ React + TypeScript frontend with Tailwind CSS
- ✅ FastAPI backend with PostgreSQL
- ✅ Sortable leaderboard with filtering
- ✅ Side-by-side model comparison
- ✅ Real-time statistics dashboard
- ✅ Cost efficiency rankings

#### 5. Runnable Examples
- ✅ Basic accuracy evaluation
- ✅ Cost analysis and comparison
- ✅ Quality metrics evaluation
- ✅ Comparative benchmarking
- ✅ MMLU benchmark runner
- 🔧 Templates for custom evaluations

#### 6. Best Practices
- ✅ Type hints and Pydantic validation
- ✅ Async/await support
- ✅ Structured logging
- ✅ Retry logic with exponential backoff
- ✅ Rate limiting
- ✅ Comprehensive error handling
- ✅ Unit and integration tests
- ✅ Pre-commit hooks
- ✅ CI/CD pipeline (GitHub Actions)

## Project Structure

```
Model_Evaluation_Toolbox/
├── config/                          # Configuration files
│   ├── api_keys.template.json       # API keys template
│   └── models_registry.json         # Model definitions & pricing
├── src/                             # Core source code
│   ├── providers/                   # API clients (OpenAI, Anthropic, etc.)
│   ├── evaluators/                  # Evaluation framework
│   │   ├── performance/             # Accuracy evaluators
│   │   ├── cost/                    # Cost analysis
│   │   ├── speed/                   # Latency benchmarks
│   │   └── quality/                 # Text quality metrics
│   ├── benchmarks/                  # Standard benchmarks (MMLU, HumanEval)
│   └── utils/                       # Utilities (logging, token counting)
├── dashboard/                       # Web dashboard
│   ├── backend/                     # FastAPI server
│   └── frontend/                    # React application
├── examples/                        # Runnable examples
├── tests/                           # Test suite
└── docs/                            # Documentation
```

## Quick Start (For You)

### 1. Setup Environment

```bash
# Navigate to project
cd Model_Evaluation_Toolbox

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -e .
```

### 2. Configure API Keys

```bash
# Copy template
cp .env.template .env

# Edit and add your API keys
nano .env
```

Add your keys:
```bash
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
GOOGLE_API_KEY=your_google_key
COHERE_API_KEY=your_cohere_key
DATABASE_URL=postgresql://user:pass@localhost/model_eval_db
```

### 3. Setup Database

```bash
# Create PostgreSQL database
createdb model_eval_db

# The tables will be created automatically on first run
```

### 4. Run Examples

```bash
# Basic evaluation
cd examples/01_basic_evaluation
python run_basic_evaluation.py

# Cost analysis
cd ../02_cost_analysis
python run_cost_analysis.py

# MMLU benchmark
cd ../06_standard_benchmarks
python run_mmlu_benchmark.py
```

### 5. Start Dashboard

**Terminal 1 - Backend:**
```bash
cd dashboard/backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd dashboard/frontend
npm install
npm start
```

Access at: http://localhost:3000

## Key Features Highlights

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
