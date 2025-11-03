"""Run Stage 3 arena-style evaluation between two models."""

import argparse
import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.evaluators.arena import ArenaPrompt, LMArenaClient
from src.lifecycle import ArenaEvaluationSuite
from src.lifecycle.models import ArenaRunConfig
from src.providers import get_client
from src.utils import setup_logging


def build_prompts() -> list[ArenaPrompt]:
    """Small playlist of prompts for arena simulations."""
    return [
        ArenaPrompt(
            prompt="Explain how to prepare a remote engineering team for an incident response drill.",
            category="operations",
        ),
        ArenaPrompt(
            prompt="Write a short story (200 words) about an astronaut discovering an unexpected lifeform on Mars.",
            category="creative",
        ),
        ArenaPrompt(
            prompt="Summarize the key similarities and differences between constitutional monarchies and parliamentary republics.",
            category="analysis",
        ),
    ]


async def main(args: argparse.Namespace) -> None:
    """Execute arena matches."""
    setup_logging(level="INFO")

    candidate_client = get_client(args.candidate_provider)
    baseline_client = get_client(args.baseline_provider)

    judge_client = None
    if args.judge_model and args.judge_provider:
        judge_client = get_client(args.judge_provider)

    arena_client = None
    if args.arena_base_url:
        arena_client = LMArenaClient(
            base_url=args.arena_base_url,
            api_key=args.arena_api_key,
        )

    suite = ArenaEvaluationSuite(
        candidate_client=candidate_client,
        candidate_model=args.candidate_model,
        baseline_client=baseline_client,
        baseline_model=args.baseline_model,
        arena_client=arena_client,
        judge_client=judge_client,
        judge_model=args.judge_model,
    )

    config = ArenaRunConfig(
        prompts=build_prompts(),
        baseline_model=args.baseline_model,
        judge_model=args.judge_model,
        judge_temperature=args.judge_temperature,
        judge_max_tokens=args.judge_max_tokens,
        arena_metadata={"experiment": args.experiment_tag},
    )

    result = await suite.run(config)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / f"{args.candidate_model}_vs_{args.baseline_model}_stage3.json"

    payload = {
        "stage": result.stage,
        "metrics": result.metrics,
        "artifacts": result.artifacts,
    }

    report_path.write_text(json.dumps(payload, indent=2))
    print(f"\nStage 3 report written to {report_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run LMArena simulation.")
    parser.add_argument("--candidate-model", default="gpt-4-turbo-2024-04-09")
    parser.add_argument("--candidate-provider", default="openai")
    parser.add_argument("--baseline-model", default="claude-3-sonnet-20240229")
    parser.add_argument("--baseline-provider", default="anthropic")
    parser.add_argument("--output-dir", default="artifacts/stage3")
    parser.add_argument("--experiment-tag", default="demo-arena")
    parser.add_argument("--judge-model", default=None)
    parser.add_argument("--judge-provider", default=None)
    parser.add_argument("--judge-temperature", type=float, default=0.0)
    parser.add_argument("--judge-max-tokens", type=int, default=256)
    parser.add_argument("--arena-base-url", default=None)
    parser.add_argument("--arena-api-key", default=None)

    args = parser.parse_args()
    asyncio.run(main(args))
