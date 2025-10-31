"""Text quality evaluation using various metrics."""

import asyncio
import time
from typing import Dict, List, Tuple
from dataclasses import dataclass

from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from rouge_score import rouge_scorer
import bert_score

from ..base_evaluator import BaseEvaluator, EvaluationResult
from ...providers.base_client import ChatMessage
from ...utils import get_logger

logger = get_logger(__name__)


@dataclass
class TextPair:
    """Pair of prompt and reference text for evaluation."""

    prompt: str
    reference: str
    context: Optional[str] = None


class TextQualityEvaluator(BaseEvaluator):
    """Evaluates text generation quality using multiple metrics."""

    def __init__(self, *args, **kwargs):
        """Initialize text quality evaluator."""
        super().__init__(*args, **kwargs)
        self.rouge_scorer = rouge_scorer.RougeScorer(
            ['rouge1', 'rouge2', 'rougeL'],
            use_stemmer=True
        )
        self.smoothing = SmoothingFunction()

    async def evaluate(
        self,
        dataset: List[TextPair],
        temperature: float = 0.7,
        max_tokens: int = 512,
        compute_bert_score: bool = False,
        **kwargs
    ) -> EvaluationResult:
        """Evaluate text generation quality.

        Args:
            dataset: List of TextPair instances with prompts and references
            temperature: Temperature for generation
            max_tokens: Maximum tokens per response
            compute_bert_score: Whether to compute BERTScore (slower)
            **kwargs: Additional parameters

        Returns:
            EvaluationResult with quality metrics
        """
        start_time = time.time()

        self.logger.info(
            f"Starting quality evaluation",
            model=self.model,
            num_samples=len(dataset)
        )

        generated_texts = []
        reference_texts = []
        bleu_scores = []
        rouge_scores = {"rouge1": [], "rouge2": [], "rougeL": []}

        # Generate responses
        for i, pair in enumerate(dataset):
            try:
                messages = [
                    ChatMessage(role="user", content=pair.prompt)
                ]

                if pair.context:
                    messages.insert(
                        0,
                        ChatMessage(role="system", content=pair.context)
                    )

                response = await self.client.chat_completion(
                    messages=messages,
                    model=self.model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )

                generated = response.content.strip()
                reference = pair.reference.strip()

                generated_texts.append(generated)
                reference_texts.append(reference)

                # Calculate BLEU score
                bleu = self._calculate_bleu(generated, reference)
                bleu_scores.append(bleu)

                # Calculate ROUGE scores
                rouge = self.rouge_scorer.score(reference, generated)
                rouge_scores["rouge1"].append(rouge["rouge1"].fmeasure)
                rouge_scores["rouge2"].append(rouge["rouge2"].fmeasure)
                rouge_scores["rougeL"].append(rouge["rougeL"].fmeasure)

                if (i + 1) % 10 == 0:
                    self.logger.info(f"Processed {i + 1}/{len(dataset)} examples")

            except Exception as e:
                self.logger.error(f"Error evaluating pair {i}", error=str(e))
                generated_texts.append("")
                reference_texts.append(pair.reference)
                bleu_scores.append(0.0)
                rouge_scores["rouge1"].append(0.0)
                rouge_scores["rouge2"].append(0.0)
                rouge_scores["rougeL"].append(0.0)

        duration = time.time() - start_time

        # Calculate aggregate metrics
        metrics = {
            "mean_bleu": sum(bleu_scores) / len(bleu_scores) if bleu_scores else 0.0,
            "mean_rouge1": sum(rouge_scores["rouge1"]) / len(rouge_scores["rouge1"]) if rouge_scores["rouge1"] else 0.0,
            "mean_rouge2": sum(rouge_scores["rouge2"]) / len(rouge_scores["rouge2"]) if rouge_scores["rouge2"] else 0.0,
            "mean_rougeL": sum(rouge_scores["rougeL"]) / len(rouge_scores["rougeL"]) if rouge_scores["rougeL"] else 0.0,
        }

        # Optionally compute BERTScore (expensive)
        if compute_bert_score and generated_texts and reference_texts:
            try:
                P, R, F1 = bert_score.score(
                    generated_texts,
                    reference_texts,
                    lang="en",
                    verbose=False
                )
                metrics["mean_bertscore_f1"] = F1.mean().item()
                metrics["mean_bertscore_precision"] = P.mean().item()
                metrics["mean_bertscore_recall"] = R.mean().item()
            except Exception as e:
                self.logger.error("Error computing BERTScore", error=str(e))

        metadata = {
            "temperature": temperature,
            "max_tokens": max_tokens,
            "compute_bert_score": compute_bert_score,
            "examples": [
                {
                    "prompt": pair.prompt[:100],
                    "generated": gen[:100],
                    "reference": ref[:100],
                    "bleu": score,
                }
                for pair, gen, ref, score in zip(
                    dataset[:5],
                    generated_texts[:5],
                    reference_texts[:5],
                    bleu_scores[:5]
                )
            ]
        }

        return self._create_result(
            metrics=metrics,
            metadata=metadata,
            duration=duration,
            num_samples=len(dataset)
        )

    def evaluate_sync(
        self,
        dataset: List[TextPair],
        temperature: float = 0.7,
        max_tokens: int = 512,
        compute_bert_score: bool = False,
        **kwargs
    ) -> EvaluationResult:
        """Synchronous version of evaluate.

        Args:
            dataset: List of TextPair instances
            temperature: Temperature for generation
            max_tokens: Maximum tokens per response
            compute_bert_score: Whether to compute BERTScore
            **kwargs: Additional parameters

        Returns:
            EvaluationResult with quality metrics
        """
        start_time = time.time()

        generated_texts = []
        reference_texts = []
        bleu_scores = []
        rouge_scores = {"rouge1": [], "rouge2": [], "rougeL": []}

        for i, pair in enumerate(dataset):
            try:
                messages = [ChatMessage(role="user", content=pair.prompt)]

                if pair.context:
                    messages.insert(0, ChatMessage(role="system", content=pair.context))

                response = self.client.chat_completion_sync(
                    messages=messages,
                    model=self.model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )

                generated = response.content.strip()
                reference = pair.reference.strip()

                generated_texts.append(generated)
                reference_texts.append(reference)

                bleu = self._calculate_bleu(generated, reference)
                bleu_scores.append(bleu)

                rouge = self.rouge_scorer.score(reference, generated)
                rouge_scores["rouge1"].append(rouge["rouge1"].fmeasure)
                rouge_scores["rouge2"].append(rouge["rouge2"].fmeasure)
                rouge_scores["rougeL"].append(rouge["rougeL"].fmeasure)

            except Exception as e:
                self.logger.error(f"Error evaluating pair {i}", error=str(e))
                generated_texts.append("")
                reference_texts.append(pair.reference)
                bleu_scores.append(0.0)

        duration = time.time() - start_time

        metrics = {
            "mean_bleu": sum(bleu_scores) / len(bleu_scores) if bleu_scores else 0.0,
            "mean_rouge1": sum(rouge_scores["rouge1"]) / len(rouge_scores["rouge1"]) if rouge_scores["rouge1"] else 0.0,
            "mean_rouge2": sum(rouge_scores["rouge2"]) / len(rouge_scores["rouge2"]) if rouge_scores["rouge2"] else 0.0,
            "mean_rougeL": sum(rouge_scores["rougeL"]) / len(rouge_scores["rougeL"]) if rouge_scores["rougeL"] else 0.0,
        }

        if compute_bert_score and generated_texts and reference_texts:
            try:
                P, R, F1 = bert_score.score(
                    generated_texts,
                    reference_texts,
                    lang="en",
                    verbose=False
                )
                metrics["mean_bertscore_f1"] = F1.mean().item()
            except Exception as e:
                self.logger.error("Error computing BERTScore", error=str(e))

        metadata = {
            "temperature": temperature,
            "max_tokens": max_tokens,
            "compute_bert_score": compute_bert_score,
        }

        return self._create_result(
            metrics=metrics,
            metadata=metadata,
            duration=duration,
            num_samples=len(dataset)
        )

    def _calculate_bleu(self, hypothesis: str, reference: str) -> float:
        """Calculate BLEU score between hypothesis and reference.

        Args:
            hypothesis: Generated text
            reference: Reference text

        Returns:
            BLEU score (0-1)
        """
        hypothesis_tokens = hypothesis.split()
        reference_tokens = [reference.split()]

        if not hypothesis_tokens or not reference_tokens[0]:
            return 0.0

        try:
            return sentence_bleu(
                reference_tokens,
                hypothesis_tokens,
                smoothing_function=self.smoothing.method1
            )
        except Exception:
            return 0.0
