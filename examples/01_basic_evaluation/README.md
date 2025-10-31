# Basic Model Evaluation

This example demonstrates how to perform a basic accuracy evaluation on a custom Q&A dataset.

## Setup

1. Ensure you have configured your API keys in `.env` or `config/api_keys.json`
2. Install dependencies: `pip install -r requirements.txt`

## Running the Example

```bash
python run_basic_evaluation.py
```

## What This Example Does

1. Creates a simple Q&A dataset
2. Evaluates a model on accuracy
3. Outputs detailed metrics including:
   - Exact match accuracy
   - Partial match accuracy
   - Per-question results
   - Total cost and duration

## Customization

Edit the script to:
- Change the model (`model="gpt-3.5-turbo"`)
- Add more questions to the dataset
- Adjust temperature and max_tokens parameters
