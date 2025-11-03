# Stage 1: Foundational Metrics

Stage 1 validates that a model is stable enough to justify deeper benchmarking. The emphasis is on deterministic, reproducible metrics that can be computed quickly on representative samples.

## Goals
- Confirm baseline competency (precision, recall, F1, accuracy).
- Measure operational characteristics (latency, throughput, cost).
- Validate guardrails (toxicity, bias probes, jailbreak attempts).

## Key Modules
- `src/lifecycle/foundational.py`: Orchestrates metric suites and aggregates results.
- `src/evaluators/performance`: Classification and QA evaluators.
- `src/evaluators/quality`: NLG quality metrics (BLEU, ROUGE, BERTScore).
- `src/evaluators/speed`: Latency benchmarking harness.
- `src/evaluators/cost`: Token and pricing analysis.

## Typical Workflow
1. Select the provider client with `src.providers.factory.get_client`.
2. Run the `FoundationalEvaluationSuite` with curated datasets or smoke-test prompts.
3. Gate models by minimum thresholds (e.g., precision ≥ 0.9, toxicity ≤ 0.02).
4. Promote passing models to Stage 2 benchmark evaluation.

## Example

```bash
python examples/lifecycle/stage1_foundational_metrics.py \
  --model gpt-4o-mini \
  --provider openai
```

This script:
- runs accuracy + F1 on a toy QA set,
- measures latency on a ping workflow,
- records token usage and estimated cost,
- emits a consolidated JSON report in `artifacts/stage1`.
