># Text Quality Metrics Example

Demonstrates evaluation using BLEU, ROUGE, and BERTScore metrics.

## Running

```bash
python run_quality_evaluation.py
```

## Metrics Computed

- BLEU: N-gram overlap between generated and reference text
- ROUGE-1/2/L: Recall-based metrics for summarization
- BERTScore: Semantic similarity using BERT embeddings (optional, slower)
