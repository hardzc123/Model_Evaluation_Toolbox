# Stage 3: Arena Evaluations (LMArena)

Arena evaluations capture fine-grained preferences by letting models compete head-to-head on curated prompts. This complements metric-driven benchmarks and provides a powerful mechanism for tie-breaking or qualitative regression detection.

## Goals
- Collect pairwise win rates with human or AI judges.
- Identify qualitative strengths and weaknesses that metrics miss.
- Maintain a rolling leaderboard to track production candidates.

## Key Modules
- `src/lifecycle/arena.py`: Orchestrates arena tournaments as part of the lifecycle pipeline.
- `src/evaluators/arena/lmarena_evaluator.py`: Integration with the LMArena API and local simulators.
- `examples/lifecycle/stage3_lmarena_simulation.py`: Demonstrates automated match scheduling and result ingestion.

## LMArena Concepts
- **Contestants**: Model endpoints or prompts you want to compare.
- **Matches**: Prompt-based battles that yield win/loss/tie outcomes.
- **Judges**: Human raters or judge models (e.g., `gpt-4o`).
- **Leaderboard**: Aggregated Elo / Bradley-Terry ranking derived from matches.

## Typical Workflow
1. Register contestants using `LMArenaClient.register_model`.
2. Create a playlist of prompts with guardrails (toxicity, jailbreak tests).
3. Use `ArenaEvaluationSuite` to schedule matches and poll results.
4. Export win-rate matrices to the dashboard or alerting systems.

## Example

```bash
python examples/lifecycle/stage3_lmarena_simulation.py \
  --candidate gpt-4o-mini \
  --baseline claude-3-haiku
```

Simulates an arena bracket locally and produces match statistics under `artifacts/stage3`.
