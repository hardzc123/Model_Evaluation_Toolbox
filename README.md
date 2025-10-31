# 🎯 AI Model Evaluation Toolbox

A comprehensive, production-ready toolkit for evaluating and benchmarking AI language models across multiple providers with a beautiful interactive dashboard.

## ✨ Features

- 🔄 **Multi-Provider Support**: OpenAI, Anthropic, Google (Gemini), Cohere, and more
- 📊 **Comprehensive Metrics**: Performance, cost, speed, quality, and safety evaluation
- 🏆 **Standard Benchmarks**: MMLU, HumanEval, and other industry-standard datasets
- 💰 **Cost Analysis**: Track token usage and calculate cost efficiency
- ⚡ **Speed Benchmarks**: Measure latency, throughput, and time-to-first-token
- 🎨 **Interactive Dashboard**: React-based UI with sorting, filtering, and visualization
- 🔒 **Production Ready**: PostgreSQL backend, proper error handling, comprehensive tests
- 📝 **Runnable Examples**: Each evaluation method includes working code samples

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- PostgreSQL 13 or higher
- Node.js 18+ (for dashboard)
- API keys for model providers you want to evaluate

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/Model_Evaluation_Toolbox.git
cd Model_Evaluation_Toolbox
```

2. **Set up Python environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
```

3. **Configure API keys**
```bash
# Copy template and add your API keys
cp .env.template .env
nano .env  # Edit with your keys

# Or use JSON config
cp config/api_keys.template.json config/api_keys.json
nano config/api_keys.json
```

4. **Set up PostgreSQL database**
```bash
# Create database
createdb model_eval_db

# Run migrations
cd dashboard/backend
alembic upgrade head
```

5. **Install dashboard frontend**
```bash
cd dashboard/frontend
npm install
```

### Running the Dashboard

**Backend (FastAPI):**
```bash
cd dashboard/backend
uvicorn app.main:app --reload --port 8000
```

**Frontend (React):**
```bash
cd dashboard/frontend
npm start
```

Access the dashboard at: `http://localhost:3000`

## 📖 Usage Examples

### Basic Evaluation

```python
from src.evaluators.performance import AccuracyEvaluator
from src.providers.openai_client import OpenAIClient

# Initialize client
client = OpenAIClient()

# Run evaluation
evaluator = AccuracyEvaluator(client, model="gpt-4")
results = evaluator.evaluate(dataset="mmlu", subset="mathematics")

print(f"Accuracy: {results['accuracy']:.2%}")
print(f"Cost: ${results['total_cost']:.4f}")
```

### Cost Analysis

```python
from src.evaluators.cost import CostAnalyzer

analyzer = CostAnalyzer()
comparison = analyzer.compare_models(
    models=["gpt-4", "claude-3-opus", "gemini-1.5-pro"],
    task_type="summarization",
    input_length=2000,
    output_length=500
)

analyzer.plot_cost_efficiency(comparison)
```

### Speed Benchmarking

```python
from src.evaluators.speed import LatencyBenchmark

benchmark = LatencyBenchmark()
results = benchmark.run(
    models=["gpt-3.5-turbo", "claude-3-haiku", "gemini-1.5-flash"],
    num_requests=100
)

print(results.summary())
```

## 📂 Project Structure

```
Model_Evaluation_Toolbox/
├── config/                      # Configuration files
│   ├── api_keys.template.json   # API keys template
│   └── models_registry.json     # Model definitions
├── src/                         # Core source code
│   ├── evaluators/              # Evaluation methods
│   │   ├── performance/         # Accuracy, precision, recall
│   │   ├── cost/                # Token usage, pricing
│   │   ├── speed/               # Latency, throughput
│   │   ├── quality/             # BLEU, ROUGE, BERTScore
│   │   └── safety/              # Toxicity, bias detection
│   ├── providers/               # API client implementations
│   ├── benchmarks/              # Standard benchmark datasets
│   └── utils/                   # Shared utilities
├── examples/                    # Runnable examples
├── dashboard/                   # Web dashboard
│   ├── backend/                 # FastAPI server
│   └── frontend/                # React application
├── tests/                       # Test suite
└── docs/                        # Documentation
```

## 🎯 Evaluation Methods

### Performance Metrics
- **Classification**: Accuracy, Precision, Recall, F1-Score
- **Generation**: BLEU, ROUGE, METEOR, BERTScore
- **Code**: Execution success rate, test pass rate
- **Math**: Exact match, numerical accuracy

### Cost Analysis
- Token counting (input/output)
- Per-request pricing calculation
- Cost-efficiency ratios
- Budget forecasting

### Speed Benchmarks
- Time to First Token (TTFT)
- Tokens per second
- End-to-end latency
- Concurrent request handling

### Quality Metrics
- Semantic similarity
- Perplexity
- Coherence scoring
- Human preference simulation

### Safety & Robustness
- Toxicity detection
- Bias evaluation
- Jailbreak resistance
- Consistency testing

## 🏆 Standard Benchmarks

- **MMLU**: Massive Multitask Language Understanding
- **HumanEval**: Code generation and execution
- **HellaSwag**: Commonsense reasoning
- **TruthfulQA**: Truthfulness evaluation
- **GSM8K**: Math problem solving
- **BBH**: Big-Bench Hard tasks

## 🎨 Dashboard Features

- 📊 **Sortable Leaderboard**: Compare models across all metrics
- 💰 **Cost Efficiency View**: Find the best value for your use case
- 📈 **Performance Charts**: Visualize benchmark results
- 🔍 **Advanced Filtering**: Filter by provider, price, speed, capabilities
- 📥 **Export Results**: Download data as CSV/JSON
- 📱 **Responsive Design**: Works on all devices

## 🔧 Configuration

### Environment Variables (.env)
```bash
OPENAI_API_KEY=your_key
ANTHROPIC_API_KEY=your_key
GOOGLE_API_KEY=your_key
COHERE_API_KEY=your_key
DATABASE_URL=postgresql://user:password@localhost/model_eval_db
```

### Models Registry (config/models_registry.json)
Configure model specifications, pricing, and capabilities.

## 🧪 Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=src --cov-report=html

# Specific test suite
pytest tests/unit/
pytest tests/integration/
```

## 📚 Documentation

Full documentation available in the `docs/` directory:
- [API Reference](docs/api_reference.md)
- [Adding New Providers](docs/adding_providers.md)
- [Custom Evaluators](docs/custom_evaluators.md)
- [Benchmark Guide](docs/benchmarks.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI, Anthropic, Google, and Cohere for their APIs
- HuggingFace for benchmark datasets
- The open-source community for evaluation metrics

## 📞 Support

- 📧 Email: support@example.com
- 💬 Discord: [Join our community](https://discord.gg/example)
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/Model_Evaluation_Toolbox/issues)

---

Made with ❤️ by the AI Evaluation Community
