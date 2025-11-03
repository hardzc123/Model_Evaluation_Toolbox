"""Accuracy evaluator for classification and question-answering tasks."""

import asyncio
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from sklearn.metrics import accuracy_score, precision_recall_fscore_support

from ..base_evaluator import BaseEvaluator, EvaluationResult
from ...providers.base_client import ChatMessage


@dataclass
class QAExample:
    """Question-answer example for evaluation."""

    question: str
    correct_answer: str
    context: Optional[str] = None
    category: Optional[str] = None


class AccuracyEvaluator(BaseEvaluator):
    """Evaluates model accuracy on Q&A or classification tasks."""

    async def evaluate(
        self,
        dataset: List[QAExample],
        temperature: float = 0.0,
        max_tokens: int = 512,
        **kwargs
    ) -> EvaluationResult:
        """Evaluate model accuracy on a dataset.

        Args:
            dataset: List of QAExample instances
            temperature: Temperature for generation
            max_tokens: Maximum tokens per response
            **kwargs: Additional parameters

        Returns:
            EvaluationResult with accuracy metrics
        """
        start_time = time.time()
        predictions = []
        ground_truth = []
        total_cost = 0.0

        self.logger.info(
            f"Starting accuracy evaluation",
            model=self.model,
            num_samples=len(dataset)
        )

        # Evaluate each example
        for i, example in enumerate(dataset):
            try:
                # Create prompt
                messages = [
                    ChatMessage(
                        role="system",
                        content="You are a helpful assistant. Answer the following question accurately and concisely."
                    ),
                ]

                if example.context:
                    messages.append(
                        ChatMessage(
                            role="user",
                            content=f"Context: {example.context}\n\nQuestion: {example.question}\n\nAnswer:"
                        )
                    )
                else:
                    messages.append(
                        ChatMessage(role="user", content=example.question)
                    )

                # Get model response
                response = await self.client.chat_completion(
                    messages=messages,
                    model=self.model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )

                predictions.append(response.content.strip().lower())
                ground_truth.append(example.correct_answer.strip().lower())

                # Calculate cost (assuming pricing is in model registry)
                if hasattr(self, '_model_pricing'):
                    cost = self.client.calculate_cost(
                        response.usage,
                        self.model,
                        self._model_pricing
                    )
                    total_cost += cost

                if (i + 1) % 10 == 0:
                    self.logger.info(f"Processed {i + 1}/{len(dataset)} examples")

            except Exception as e:
                self.logger.error(
                    f"Error evaluating example {i}",
                    error=str(e)
                )
                predictions.append("")
                ground_truth.append(example.correct_answer.strip().lower())

        # Calculate metrics
        duration = time.time() - start_time

        # Exact match accuracy
        exact_matches = sum(
            1 for pred, truth in zip(predictions, ground_truth)
            if pred == truth
        )
        accuracy = exact_matches / len(dataset) if dataset else 0.0

        # Partial match (contains correct answer)
        partial_matches = sum(
            1 for pred, truth in zip(predictions, ground_truth)
            if truth in pred
        )
        partial_accuracy = partial_matches / len(dataset) if dataset else 0.0

        metrics = {
            "accuracy": accuracy,
            "partial_accuracy": partial_accuracy,
            "exact_matches": exact_matches,
            "partial_matches": partial_matches,
            "total_samples": len(dataset),
        }

        metadata = {
            "temperature": temperature,
            "max_tokens": max_tokens,
            "examples": [
                {
                    "question": ex.question[:100],
                    "predicted": pred[:100],
                    "actual": truth[:100],
                }
                for ex, pred, truth in zip(dataset[:5], predictions[:5], ground_truth[:5])
            ]
        }

        return self._create_result(
            metrics=metrics,
            metadata=metadata,
            duration=duration,
            total_cost=total_cost,
            num_samples=len(dataset)
        )

    def evaluate_sync(
        self,
        dataset: List[QAExample],
        temperature: float = 0.0,
        max_tokens: int = 512,
        **kwargs
    ) -> EvaluationResult:
        """Synchronous version of evaluate.

        Args:
            dataset: List of QAExample instances
            temperature: Temperature for generation
            max_tokens: Maximum tokens per response
            **kwargs: Additional parameters

        Returns:
            EvaluationResult with accuracy metrics
        """
        start_time = time.time()
        predictions = []
        ground_truth = []
        total_cost = 0.0

        for i, example in enumerate(dataset):
            try:
                messages = [
                    ChatMessage(
                        role="system",
                        content="You are a helpful assistant. Answer the following question accurately and concisely."
                    ),
                ]

                if example.context:
                    messages.append(
                        ChatMessage(
                            role="user",
                            content=f"Context: {example.context}\n\nQuestion: {example.question}\n\nAnswer:"
                        )
                    )
                else:
                    messages.append(
                        ChatMessage(role="user", content=example.question)
                    )

                response = self.client.chat_completion_sync(
                    messages=messages,
                    model=self.model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )

                predictions.append(response.content.strip().lower())
                ground_truth.append(example.correct_answer.strip().lower())

            except Exception as e:
                self.logger.error(f"Error evaluating example {i}", error=str(e))
                predictions.append("")
                ground_truth.append(example.correct_answer.strip().lower())

        duration = time.time() - start_time

        exact_matches = sum(
            1 for pred, truth in zip(predictions, ground_truth)
            if pred == truth
        )
        accuracy = exact_matches / len(dataset) if dataset else 0.0

        partial_matches = sum(
            1 for pred, truth in zip(predictions, ground_truth)
            if truth in pred
        )
        partial_accuracy = partial_matches / len(dataset) if dataset else 0.0

        metrics = {
            "accuracy": accuracy,
            "partial_accuracy": partial_accuracy,
            "exact_matches": exact_matches,
            "partial_matches": partial_matches,
            "total_samples": len(dataset),
        }

        metadata = {
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        return self._create_result(
            metrics=metrics,
            metadata=metadata,
            duration=duration,
            total_cost=total_cost,
            num_samples=len(dataset)
        )
