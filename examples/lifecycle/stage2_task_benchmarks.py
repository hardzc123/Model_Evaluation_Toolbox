"""Run Stage 2 task/domain benchmarks for a model."""

import argparse
import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.lifecycle import BenchmarkEvaluationSuite
from src.lifecycle.models import BenchmarkRunConfig
from src.providers import get_client
from src.utils import setup_logging


async def main(args: argparse.Namespace) -> None:
    """Execute benchmark suite for the requested model."""
    setup_logging(level="INFO")
    client = get_client(args.provider)

    suite = BenchmarkEvaluationSuite(
        client=client,
        model=args.model,
    )

    benchmark_kwargs = {}
    if args.mmlu_samples:
        benchmark_kwargs.setdefault("mmlu", {})["num_samples_per_subject"] = args.mmlu_samples
    if args.mmlu_subjects:
        benchmark_kwargs.setdefault("mmlu", {})["subjects"] = args.mmlu_subjects
    if args.humaneval_samples:
        benchmark_kwargs.setdefault("humaneval", {})["num_samples"] = args.humaneval_samples

    config = BenchmarkRunConfig(
        benchmark_names=args.benchmarks,
        benchmark_kwargs=benchmark_kwargs,
    )

    result = await suite.run(config)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / f"{args.model}_stage2.json"

    payload = {
        "stage": result.stage,
        "metrics": result.metrics,
        "artifacts": result.artifacts,
    }

    report_path.write_text(json.dumps(payload, indent=2))
    print(f"\nStage 2 report written to {report_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run benchmark evaluations.")
    parser.add_argument("--model", default="gpt-4-turbo-2024-04-09")
    parser.add_argument("--provider", default="openai")
    parser.add_argument("--output-dir", default="artifacts/stage2")
    parser.add_argument(
        "--benchmarks",
        nargs="+",
        default=["mmlu", "humaneval"],
        help="List of benchmarks to run (mmlu, humaneval).",
    )
    parser.add_argument("--mmlu-samples", type=int, default=25)
    parser.add_argument(
        "--mmlu-subjects",
        nargs="*",
        default=None,
        help="Subset of MMLU subjects.",
    )
    parser.add_argument("--humaneval-samples", type=int, default=25)

    args = parser.parse_args()
    asyncio.run(main(args))
