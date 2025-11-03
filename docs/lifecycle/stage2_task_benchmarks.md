# Stage 2: Task & Domain Benchmarks

Stage 2 validates short-listed models against standardized benchmarks that approximate real deployments. The goal is to establish a comparable scorecard and surface domain regressions before production pilots.

## Goals
- Quantify task-level competence with reproducible datasets.
- Compare multiple models side-by-side on the same benchmark.
- Track longitudinal performance across releases.

## Key Modules
- `src/lifecycle/benchmarks.py`: High-level orchestrator for benchmark suites.
- `src/benchmarks/mmlu_benchmark.py`: General knowledge evaluation.
- `src/benchmarks/humaneval_benchmark.py`: Code generation & execution checks.
- `examples/lifecycle/stage2_task_benchmarks.py`: Sample script for running multiple benchmarks sequentially.

## Typical Workflow
1. Promote candidates from Stage 1.
2. Choose benchmarks aligned with your use case (e.g., MMLU for knowledge, GSM8K for math).
3. Run `BenchmarkEvaluationSuite` to execute selected datasets.
4. Export results to the dashboard or data warehouse for trend analysis.

## Example

```bash
python examples/lifecycle/stage2_task_benchmarks.py \
  --model gpt-4o \
  --provider openai \
  --benchmarks mmlu gsm8k
```

Generates per-benchmark JSON artifacts under `artifacts/stage2`.
