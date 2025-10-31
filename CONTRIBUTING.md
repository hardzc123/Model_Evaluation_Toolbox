# Contributing to Model Evaluation Toolbox

Thank you for your interest in contributing! This document provides guidelines and instructions.

## Development Setup

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/Model_Evaluation_Toolbox.git`
3. Create a virtual environment: `python -m venv venv`
4. Install dependencies: `pip install -r requirements.txt`
5. Install pre-commit hooks: `pre-commit install`

## Code Standards

### Python

- Follow PEP 8 style guide
- Use type hints for function signatures
- Write docstrings (Google style) for all public functions
- Keep functions focused and single-purpose
- Maximum line length: 100 characters

### Testing

- Write tests for all new features
- Maintain >80% code coverage
- Use pytest for testing
- Mock external API calls

### Commit Messages

Follow conventional commits:
- `feat: Add new evaluation metric`
- `fix: Correct token counting for Anthropic`
- `docs: Update API documentation`
- `test: Add tests for cost analyzer`
- `refactor: Simplify provider factory`

## Pull Request Process

1. Create a feature branch: `git checkout -b feature/your-feature-name`
2. Make your changes and commit
3. Write/update tests
4. Run tests: `pytest`
5. Run linters: `ruff check src/ && black src/`
6. Push and create a pull request
7. Ensure CI passes
8. Request review

## Adding New Features

### Adding a New Model Provider

1. Create a new client in `src/providers/`
2. Inherit from `BaseClient`
3. Implement required methods
4. Add to factory in `src/providers/factory.py`
5. Update models registry
6. Write tests

### Adding a New Evaluator

1. Create module in `src/evaluators/`
2. Inherit from `BaseEvaluator`
3. Implement `evaluate()` and `evaluate_sync()`
4. Write comprehensive tests
5. Add example usage

### Adding a New Benchmark

1. Create module in `src/benchmarks/`
2. Integrate with HuggingFace datasets or custom loader
3. Follow existing benchmark patterns
4. Document dataset requirements

## Documentation

- Update README.md for new features
- Add docstrings to all public APIs
- Create examples for new functionality
- Update QUICKSTART.md if setup changes

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_config.py
```

## Code Review

We look for:
- Code quality and style
- Test coverage
- Documentation
- Performance considerations
- Security implications

## Questions?

Open an issue or start a discussion on GitHub.
