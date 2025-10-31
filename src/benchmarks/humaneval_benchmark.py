"""HumanEval benchmark for code generation."""

import time
from typing import List, Optional, Dict, Any
from datasets import load_dataset

from ..evaluators.base_evaluator import BaseEvaluator, EvaluationResult
from ..providers.base_client import ChatMessage
from ...utils import get_logger

logger = get_logger(__name__)


class HumanEvalBenchmark(BaseEvaluator):
    """Evaluates models on the HumanEval code generation benchmark."""

    async def evaluate(
        self,
        num_samples: Optional[int] = None,
        temperature: float = 0.0,
        **kwargs
    ) -> EvaluationResult:
        """Evaluate model on HumanEval benchmark.

        Args:
            num_samples: Number of samples to evaluate (None = all)
            temperature: Temperature for code generation
            **kwargs: Additional parameters

        Returns:
            EvaluationResult with HumanEval scores
        """
        start_time = time.time()

        self.logger.info(
            f"Starting HumanEval evaluation",
            model=self.model,
            num_samples=num_samples or "all"
        )

        try:
            # Load HumanEval dataset
            dataset = load_dataset("openai_humaneval", split="test")

            if num_samples:
                samples = list(dataset)[:num_samples]
            else:
                samples = list(dataset)

            correct = 0
            total = len(samples)
            results = []

            for i, sample in enumerate(samples):
                try:
                    task_id = sample["task_id"]
                    prompt = sample["prompt"]
                    canonical_solution = sample["canonical_solution"]
                    test = sample["test"]

                    # Generate code
                    messages = [
                        ChatMessage(
                            role="system",
                            content="You are an expert Python programmer. Complete the function exactly as requested."
                        ),
                        ChatMessage(
                            role="user",
                            content=f"{prompt}\n\nProvide only the function implementation without explanation."
                        )
                    ]

                    response = await self.client.chat_completion(
                        messages=messages,
                        model=self.model,
                        temperature=temperature,
                        max_tokens=512,
                    )

                    generated_code = self._extract_code(response.content)

                    # Test the generated code
                    passed = self._test_code(generated_code, test, prompt)

                    if passed:
                        correct += 1

                    results.append({
                        "task_id": task_id,
                        "passed": passed,
                        "generated_code": generated_code[:200],
                    })

                    if (i + 1) % 10 == 0:
                        self.logger.info(
                            f"Processed {i + 1}/{total} samples",
                            pass_rate=correct / (i + 1)
                        )

                except Exception as e:
                    self.logger.error(f"Error on sample {i}", error=str(e))
                    results.append({
                        "task_id": sample.get("task_id", f"sample_{i}"),
                        "passed": False,
                        "error": str(e)
                    })

            duration = time.time() - start_time

            pass_rate = correct / total if total > 0 else 0.0

            metrics = {
                "pass_rate": pass_rate,
                "passed_tests": correct,
                "total_tests": total,
            }

            metadata = {
                "temperature": temperature,
                "sample_results": results[:10],  # First 10 for reference
            }

            return self._create_result(
                metrics=metrics,
                metadata=metadata,
                duration=duration,
                num_samples=total
            )

        except Exception as e:
            self.logger.error("Failed to load HumanEval dataset", error=str(e))
            raise

    def evaluate_sync(
        self,
        num_samples: Optional[int] = None,
        temperature: float = 0.0,
        **kwargs
    ) -> EvaluationResult:
        """Synchronous HumanEval evaluation.

        Args:
            num_samples: Number of samples to evaluate
            temperature: Temperature for code generation
            **kwargs: Additional parameters

        Returns:
            EvaluationResult with HumanEval scores
        """
        start_time = time.time()

        dataset = load_dataset("openai_humaneval", split="test")

        if num_samples:
            samples = list(dataset)[:num_samples]
        else:
            samples = list(dataset)

        correct = 0
        total = len(samples)

        for i, sample in enumerate(samples):
            try:
                prompt = sample["prompt"]
                test = sample["test"]

                messages = [
                    ChatMessage(
                        role="system",
                        content="You are an expert Python programmer."
                    ),
                    ChatMessage(
                        role="user",
                        content=f"{prompt}\n\nProvide only the function implementation."
                    )
                ]

                response = self.client.chat_completion_sync(
                    messages=messages,
                    model=self.model,
                    temperature=temperature,
                    max_tokens=512,
                )

                generated_code = self._extract_code(response.content)
                passed = self._test_code(generated_code, test, prompt)

                if passed:
                    correct += 1

            except Exception as e:
                self.logger.error(f"Error on sample {i}", error=str(e))

        duration = time.time() - start_time
        pass_rate = correct / total if total > 0 else 0.0

        metrics = {
            "pass_rate": pass_rate,
            "passed_tests": correct,
            "total_tests": total,
        }

        metadata = {
            "temperature": temperature,
        }

        return self._create_result(
            metrics=metrics,
            metadata=metadata,
            duration=duration,
            num_samples=total
        )

    def _extract_code(self, response: str) -> str:
        """Extract code from model response.

        Args:
            response: Model response

        Returns:
            Extracted code
        """
        # Try to find code between ```python and ```
        if "```python" in response:
            parts = response.split("```python")
            if len(parts) > 1:
                code = parts[1].split("```")[0]
                return code.strip()

        # Try generic code blocks
        if "```" in response:
            parts = response.split("```")
            if len(parts) > 1:
                return parts[1].strip()

        # Return as-is if no code blocks found
        return response.strip()

    def _test_code(self, code: str, test: str, prompt: str) -> bool:
        """Test generated code against test cases.

        Args:
            code: Generated code
            test: Test code
            prompt: Original prompt

        Returns:
            True if all tests pass
        """
        try:
            # Create test environment
            exec_globals = {}

            # Execute the code
            full_code = prompt + "\n" + code
            exec(full_code, exec_globals)

            # Execute tests
            exec(test, exec_globals)

            return True

        except Exception as e:
            return False
