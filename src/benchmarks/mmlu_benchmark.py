"""MMLU (Massive Multitask Language Understanding) benchmark implementation."""

import asyncio
from typing import List, Dict, Optional
from datasets import load_dataset

from ..evaluators.base_evaluator import BaseEvaluator, EvaluationResult
from ..providers.base_client import ChatMessage
from ...utils import get_logger

logger = get_logger(__name__)


class MMLUBenchmark(BaseEvaluator):
    """Evaluates models on the MMLU benchmark."""

    SUBJECTS = [
        "abstract_algebra", "anatomy", "astronomy", "business_ethics",
        "clinical_knowledge", "college_biology", "college_chemistry",
        "college_computer_science", "college_mathematics", "college_medicine",
        "college_physics", "computer_security", "conceptual_physics",
        "econometrics", "electrical_engineering", "elementary_mathematics",
        "formal_logic", "global_facts", "high_school_biology",
        "high_school_chemistry", "high_school_computer_science",
        "high_school_european_history", "high_school_geography",
        "high_school_government_and_politics", "high_school_macroeconomics",
        "high_school_mathematics", "high_school_microeconomics",
        "high_school_physics", "high_school_psychology", "high_school_statistics",
        "high_school_us_history", "high_school_world_history", "human_aging",
        "human_sexuality", "international_law", "jurisprudence",
        "logical_fallacies", "machine_learning", "management", "marketing",
        "medical_genetics", "miscellaneous", "moral_disputes", "moral_scenarios",
        "nutrition", "philosophy", "prehistory", "professional_accounting",
        "professional_law", "professional_medicine", "professional_psychology",
        "public_relations", "security_studies", "sociology", "us_foreign_policy",
        "virology", "world_religions"
    ]

    async def evaluate(
        self,
        subjects: Optional[List[str]] = None,
        num_samples_per_subject: int = 100,
        **kwargs
    ) -> EvaluationResult:
        """Evaluate model on MMLU benchmark.

        Args:
            subjects: List of MMLU subjects to evaluate (default: all)
            num_samples_per_subject: Number of samples per subject
            **kwargs: Additional parameters

        Returns:
            EvaluationResult with MMLU scores
        """
        import time
        start_time = time.time()

        if subjects is None:
            subjects = self.SUBJECTS[:10]  # Start with subset for testing

        self.logger.info(
            f"Starting MMLU evaluation",
            model=self.model,
            subjects=len(subjects)
        )

        all_results = []
        subject_scores = {}

        for subject in subjects:
            try:
                # Load dataset for this subject
                dataset = load_dataset("cais/mmlu", subject, split="test")

                # Limit samples
                samples = list(dataset)[:num_samples_per_subject]

                correct = 0
                total = len(samples)

                for sample in samples:
                    question = sample["question"]
                    choices = sample["choices"]
                    answer_idx = sample["answer"]

                    # Format prompt
                    prompt = self._format_mmlu_prompt(question, choices)

                    messages = [
                        ChatMessage(role="system", content="You are a helpful assistant that answers multiple choice questions accurately."),
                        ChatMessage(role="user", content=prompt)
                    ]

                    try:
                        response = await self.client.chat_completion(
                            messages=messages,
                            model=self.model,
                            temperature=0.0,
                            max_tokens=10,
                        )

                        # Extract answer (A, B, C, or D)
                        predicted_answer = self._extract_answer(response.content)
                        correct_answer = ["A", "B", "C", "D"][answer_idx]

                        if predicted_answer == correct_answer:
                            correct += 1

                    except Exception as e:
                        self.logger.warning(f"Error on question", error=str(e))

                accuracy = correct / total if total > 0 else 0.0
                subject_scores[subject] = accuracy

                self.logger.info(
                    f"Completed {subject}",
                    accuracy=accuracy,
                    correct=correct,
                    total=total
                )

            except Exception as e:
                self.logger.error(f"Error loading subject {subject}", error=str(e))
                subject_scores[subject] = 0.0

        duration = time.time() - start_time

        # Calculate overall metrics
        overall_accuracy = sum(subject_scores.values()) / len(subject_scores) if subject_scores else 0.0

        metrics = {
            "overall_accuracy": overall_accuracy,
            "num_subjects": len(subjects),
            "subject_scores": subject_scores,
        }

        metadata = {
            "subjects_evaluated": subjects,
            "num_samples_per_subject": num_samples_per_subject,
        }

        return self._create_result(
            metrics=metrics,
            metadata=metadata,
            duration=duration,
            num_samples=len(subjects) * num_samples_per_subject
        )

    def evaluate_sync(
        self,
        subjects: Optional[List[str]] = None,
        num_samples_per_subject: int = 100,
        **kwargs
    ) -> EvaluationResult:
        """Synchronous MMLU evaluation.

        Args:
            subjects: List of subjects to evaluate
            num_samples_per_subject: Samples per subject
            **kwargs: Additional parameters

        Returns:
            EvaluationResult with MMLU scores
        """
        import time
        start_time = time.time()

        if subjects is None:
            subjects = self.SUBJECTS[:10]

        subject_scores = {}

        for subject in subjects:
            try:
                dataset = load_dataset("cais/mmlu", subject, split="test")
                samples = list(dataset)[:num_samples_per_subject]

                correct = 0
                total = len(samples)

                for sample in samples:
                    question = sample["question"]
                    choices = sample["choices"]
                    answer_idx = sample["answer"]

                    prompt = self._format_mmlu_prompt(question, choices)
                    messages = [
                        ChatMessage(role="system", content="You are a helpful assistant."),
                        ChatMessage(role="user", content=prompt)
                    ]

                    try:
                        response = self.client.chat_completion_sync(
                            messages=messages,
                            model=self.model,
                            temperature=0.0,
                            max_tokens=10,
                        )

                        predicted_answer = self._extract_answer(response.content)
                        correct_answer = ["A", "B", "C", "D"][answer_idx]

                        if predicted_answer == correct_answer:
                            correct += 1

                    except Exception as e:
                        self.logger.warning(f"Error on question", error=str(e))

                accuracy = correct / total if total > 0 else 0.0
                subject_scores[subject] = accuracy

            except Exception as e:
                self.logger.error(f"Error loading subject {subject}", error=str(e))
                subject_scores[subject] = 0.0

        duration = time.time() - start_time

        overall_accuracy = sum(subject_scores.values()) / len(subject_scores) if subject_scores else 0.0

        metrics = {
            "overall_accuracy": overall_accuracy,
            "num_subjects": len(subjects),
            "subject_scores": subject_scores,
        }

        metadata = {
            "subjects_evaluated": subjects,
            "num_samples_per_subject": num_samples_per_subject,
        }

        return self._create_result(
            metrics=metrics,
            metadata=metadata,
            duration=duration,
            num_samples=len(subjects) * num_samples_per_subject
        )

    def _format_mmlu_prompt(self, question: str, choices: List[str]) -> str:
        """Format MMLU question as prompt.

        Args:
            question: The question text
            choices: List of answer choices

        Returns:
            Formatted prompt string
        """
        prompt = f"{question}\n\n"
        for i, choice in enumerate(choices):
            letter = ["A", "B", "C", "D"][i]
            prompt += f"{letter}. {choice}\n"
        prompt += "\nAnswer with just the letter (A, B, C, or D):"
        return prompt

    def _extract_answer(self, response: str) -> Optional[str]:
        """Extract answer letter from response.

        Args:
            response: Model response

        Returns:
            Answer letter (A, B, C, or D) or None
        """
        response = response.strip().upper()

        # Try to find a single letter
        for letter in ["A", "B", "C", "D"]:
            if letter in response[:10]:  # Check first 10 characters
                return letter

        return None
