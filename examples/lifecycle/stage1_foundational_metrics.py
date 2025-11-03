"""Run Stage 1 foundational metrics for a single model."""

import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import List

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.evaluators.performance.accuracy_evaluator import QAExample
from src.evaluators.quality.text_quality_evaluator import TextPair
from src.lifecycle import FoundationalEvaluationSuite
from src.lifecycle.models import FoundationalRunConfig
from src.providers import get_client
from src.utils import setup_logging


def build_accuracy_dataset() -> List[QAExample]:
    """Small smoke-test dataset for accuracy metrics."""
    return [
        QAExample(question="What is the capital of Japan?", correct_answer="Tokyo"),
        QAExample(question="What is 9 * 7?", correct_answer="63"),
        QAExample(
            question="Who is the author of 'Pride and Prejudice'?",
            correct_answer="Jane Austen",
        ),
        QAExample(
            question="Which planet is known as the Red Planet?",
            correct_answer="Mars",
        ),
        QAExample(
            question="What is the chemical symbol for water?",
            correct_answer="H2O",
        ),
    ]


def build_quality_dataset() -> List[TextPair]:
    """Reference dataset for BLEU/ROUGE smoke tests."""
    return [
        TextPair(
            prompt="Write a 2 sentence summary of the Eiffel Tower.",
            reference="The Eiffel Tower is a wrought-iron lattice tower in Paris that was built for the 1889 World's Fair. It has become an enduring global symbol of France and innovative engineering.",
        ),
        TextPair(
            prompt="Describe the benefits of code review in software teams.",
            reference="Code review helps teams catch bugs early, share knowledge, and maintain consistent coding standards. It also encourages collaboration and increases overall code quality.",
        ),
    ]


async def main(args: argparse.Namespace) -> None:
    """Execute Stage 1 for the requested model."""
    setup_logging(level="INFO")

    client = get_client(args.provider)

    suite = FoundationalEvaluationSuite(
        client=client,
        model=args.model,
    )

    config = FoundationalRunConfig(
        accuracy_dataset=build_accuracy_dataset(),
        quality_dataset=build_quality_dataset(),
        compute_bert_score=args.compute_bert_score,
        latency_requests=args.latency_requests,
        latency_prompt=args.latency_prompt,
        latency_max_tokens=args.latency_max_tokens,
        latency_concurrency=args.latency_concurrency,
        cost_model_ids=args.cost_models or [args.model],
        cost_input_tokens=args.cost_input_tokens,
        cost_output_tokens=args.cost_output_tokens,
        cost_requests_per_day=args.cost_requests_per_day,
    )

    result = await suite.run(config)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / f"{args.model}_stage1.json"

    payload = {
        "stage": result.stage,
        "metrics": result.metrics,
        "artifacts": result.artifacts,
    }

    report_path.write_text(json.dumps(payload, indent=2))
    print(f"\nStage 1 report written to {report_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run foundational metrics.")
    parser.add_argument("--model", default="gpt-4-turbo-2024-04-09")
    parser.add_argument("--provider", default="openai")
    parser.add_argument("--output-dir", default="artifacts/stage1")
    parser.add_argument("--compute-bert-score", action="store_true")
    parser.add_argument("--latency-requests", type=int, default=10)
    parser.add_argument(
        "--latency-prompt",
        default="Provide a concise summary of the 2024 AI safety landscape.",
    )
    parser.add_argument("--latency-max-tokens", type=int, default=256)
    parser.add_argument("--latency-concurrency", type=int, default=1)
    parser.add_argument("--cost-models", nargs="*", default=None)
    parser.add_argument("--cost-input-tokens", type=int, default=1000)
    parser.add_argument("--cost-output-tokens", type=int, default=250)
    parser.add_argument("--cost-requests-per-day", type=int, default=1000)

    args = parser.parse_args()
    asyncio.run(main(args))
