"""Latency and throughput benchmarking for models."""

import asyncio
import time
from dataclasses import dataclass
from typing import List, Optional
import statistics

from ..base_evaluator import BaseEvaluator, EvaluationResult
from ...providers.base_client import ChatMessage
from ...utils import get_logger

logger = get_logger(__name__)


@dataclass
class LatencyMetrics:
    """Latency metrics for a model."""

    mean_latency: float
    median_latency: float
    p95_latency: float
    p99_latency: float
    min_latency: float
    max_latency: float
    throughput: float  # requests per second
    tokens_per_second: Optional[float] = None


class LatencyBenchmark(BaseEvaluator):
    """Benchmarks model latency and throughput."""

    async def evaluate(
        self,
        num_requests: int = 100,
        prompt: str = "Tell me a short story about a robot.",
        max_tokens: int = 256,
        concurrent_requests: int = 1,
        **kwargs
    ) -> EvaluationResult:
        """Benchmark model latency and throughput.

        Args:
            num_requests: Number of requests to make
            prompt: Test prompt to use
            max_tokens: Maximum tokens per response
            concurrent_requests: Number of concurrent requests
            **kwargs: Additional parameters

        Returns:
            EvaluationResult with latency metrics
        """
        self.logger.info(
            f"Starting latency benchmark",
            model=self.model,
            num_requests=num_requests,
            concurrent_requests=concurrent_requests
        )

        messages = [ChatMessage(role="user", content=prompt)]
        latencies = []
        total_tokens = 0
        total_time_start = time.time()

        # Run requests in batches based on concurrent_requests
        for batch_start in range(0, num_requests, concurrent_requests):
            batch_size = min(concurrent_requests, num_requests - batch_start)
            tasks = []

            for _ in range(batch_size):
                tasks.append(self._single_request(messages, max_tokens))

            # Execute batch concurrently
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)

            for result in batch_results:
                if isinstance(result, Exception):
                    self.logger.warning(f"Request failed", error=str(result))
                else:
                    latencies.append(result["latency"])
                    total_tokens += result["tokens"]

            # Log progress
            completed = len(latencies)
            if completed % 10 == 0:
                self.logger.info(f"Completed {completed}/{num_requests} requests")

        total_duration = time.time() - total_time_start

        # Calculate metrics
        if latencies:
            latency_metrics = LatencyMetrics(
                mean_latency=statistics.mean(latencies),
                median_latency=statistics.median(latencies),
                p95_latency=self._percentile(latencies, 95),
                p99_latency=self._percentile(latencies, 99),
                min_latency=min(latencies),
                max_latency=max(latencies),
                throughput=len(latencies) / total_duration,
                tokens_per_second=total_tokens / total_duration if total_tokens > 0 else None,
            )
        else:
            # Handle case where all requests failed
            latency_metrics = LatencyMetrics(
                mean_latency=0,
                median_latency=0,
                p95_latency=0,
                p99_latency=0,
                min_latency=0,
                max_latency=0,
                throughput=0,
                tokens_per_second=0,
            )

        metrics = {
            "mean_latency_ms": latency_metrics.mean_latency * 1000,
            "median_latency_ms": latency_metrics.median_latency * 1000,
            "p95_latency_ms": latency_metrics.p95_latency * 1000,
            "p99_latency_ms": latency_metrics.p99_latency * 1000,
            "min_latency_ms": latency_metrics.min_latency * 1000,
            "max_latency_ms": latency_metrics.max_latency * 1000,
            "throughput_rps": latency_metrics.throughput,
            "tokens_per_second": latency_metrics.tokens_per_second,
            "successful_requests": len(latencies),
            "failed_requests": num_requests - len(latencies),
        }

        metadata = {
            "num_requests": num_requests,
            "concurrent_requests": concurrent_requests,
            "prompt": prompt[:100],
            "max_tokens": max_tokens,
        }

        return self._create_result(
            metrics=metrics,
            metadata=metadata,
            duration=total_duration,
            num_samples=num_requests
        )

    def evaluate_sync(
        self,
        num_requests: int = 100,
        prompt: str = "Tell me a short story about a robot.",
        max_tokens: int = 256,
        **kwargs
    ) -> EvaluationResult:
        """Synchronous latency benchmark.

        Args:
            num_requests: Number of requests to make
            prompt: Test prompt to use
            max_tokens: Maximum tokens per response
            **kwargs: Additional parameters

        Returns:
            EvaluationResult with latency metrics
        """
        messages = [ChatMessage(role="user", content=prompt)]
        latencies = []
        total_tokens = 0
        total_time_start = time.time()

        for i in range(num_requests):
            start_time = time.time()
            try:
                response = self.client.chat_completion_sync(
                    messages=messages,
                    model=self.model,
                    max_tokens=max_tokens,
                )

                latency = time.time() - start_time
                latencies.append(latency)
                total_tokens += response.usage.total_tokens

                if (i + 1) % 10 == 0:
                    self.logger.info(f"Completed {i + 1}/{num_requests} requests")

            except Exception as e:
                self.logger.warning(f"Request {i} failed", error=str(e))

        total_duration = time.time() - total_time_start

        if latencies:
            latency_metrics = LatencyMetrics(
                mean_latency=statistics.mean(latencies),
                median_latency=statistics.median(latencies),
                p95_latency=self._percentile(latencies, 95),
                p99_latency=self._percentile(latencies, 99),
                min_latency=min(latencies),
                max_latency=max(latencies),
                throughput=len(latencies) / total_duration,
                tokens_per_second=total_tokens / total_duration if total_tokens > 0 else None,
            )
        else:
            latency_metrics = LatencyMetrics(
                mean_latency=0,
                median_latency=0,
                p95_latency=0,
                p99_latency=0,
                min_latency=0,
                max_latency=0,
                throughput=0,
                tokens_per_second=0,
            )

        metrics = {
            "mean_latency_ms": latency_metrics.mean_latency * 1000,
            "median_latency_ms": latency_metrics.median_latency * 1000,
            "p95_latency_ms": latency_metrics.p95_latency * 1000,
            "p99_latency_ms": latency_metrics.p99_latency * 1000,
            "min_latency_ms": latency_metrics.min_latency * 1000,
            "max_latency_ms": latency_metrics.max_latency * 1000,
            "throughput_rps": latency_metrics.throughput,
            "tokens_per_second": latency_metrics.tokens_per_second,
            "successful_requests": len(latencies),
            "failed_requests": num_requests - len(latencies),
        }

        metadata = {
            "num_requests": num_requests,
            "prompt": prompt[:100],
            "max_tokens": max_tokens,
        }

        return self._create_result(
            metrics=metrics,
            metadata=metadata,
            duration=total_duration,
            num_samples=num_requests
        )

    async def _single_request(self, messages: List[ChatMessage], max_tokens: int) -> dict:
        """Execute a single request and measure latency.

        Args:
            messages: Messages to send
            max_tokens: Maximum tokens

        Returns:
            Dictionary with latency and token count
        """
        start_time = time.time()
        response = await self.client.chat_completion(
            messages=messages,
            model=self.model,
            max_tokens=max_tokens,
        )
        latency = time.time() - start_time

        return {
            "latency": latency,
            "tokens": response.usage.total_tokens
        }

    @staticmethod
    def _percentile(data: List[float], percentile: float) -> float:
        """Calculate percentile of data.

        Args:
            data: List of values
            percentile: Percentile to calculate (0-100)

        Returns:
            Percentile value
        """
        sorted_data = sorted(data)
        index = int(len(sorted_data) * (percentile / 100))
        return sorted_data[min(index, len(sorted_data) - 1)]
