"""LMArena integration and local arena simulations."""

from __future__ import annotations

import json
from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Any, Dict, Optional, Sequence

import httpx

from ..base_evaluator import BaseEvaluator, EvaluationResult
from ...providers.base_client import BaseClient, ChatMessage
from ...utils import get_logger

logger = get_logger(__name__)


@dataclass
class ArenaPrompt:
    """Prompt used for arena matches."""

    prompt: str
    category: Optional[str] = None
    reference: Optional[str] = None
    metadata: Dict[str, Any] = None


@dataclass
class ArenaMatchSummary:
    """Summary of an arena match."""

    prompt: str
    winner: str
    confidence: float
    judge: str
    reason: str
    candidate_response: str
    baseline_response: str
    metadata: Dict[str, Any]


class LMArenaClient:
    """Thin async wrapper for the LMArena API."""

    def __init__(
        self,
        base_url: str,
        api_key: Optional[str] = None,
        timeout: float = 30.0,
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout

    async def submit_match(
        self,
        prompt: ArenaPrompt,
        candidate_response: str,
        baseline_response: str,
        judge_model: Optional[str] = None,
        extra_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Submit a match to the arena API."""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        payload = {
            "prompt": prompt.prompt,
            "category": prompt.category,
            "reference": prompt.reference,
            "candidate_response": candidate_response,
            "baseline_response": baseline_response,
            "judge_model": judge_model,
            "metadata": {
                **(prompt.metadata or {}),
                **(extra_metadata or {}),
            },
        }

        url = f"{self.base_url}/api/v1/matches"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()


class LMArenaEvaluator(BaseEvaluator):
    """Runs arena-style evaluations between two models."""

    def __init__(
        self,
        client: BaseClient,
        model: str,
        baseline_client: BaseClient,
        baseline_model: str,
        arena_client: Optional[LMArenaClient] = None,
        judge_client: Optional[BaseClient] = None,
        judge_model: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(client, model, **kwargs)
        self.baseline_client = baseline_client
        self.baseline_model = baseline_model
        self.arena_client = arena_client
        self.judge_client = judge_client
        self.judge_model = judge_model

    async def evaluate(
        self,
        dataset: Sequence[ArenaPrompt],
        judge_temperature: float = 0.0,
        judge_max_tokens: int = 256,
        **kwargs,
    ) -> EvaluationResult:
        """Run arena matches for prompts in the dataset."""
        candidate_wins = 0
        baseline_wins = 0
        ties = 0
        match_summaries = []

        for prompt in dataset:
            candidate_response = await self._generate_response(
                self.client,
                self.model,
                prompt.prompt
            )
            baseline_response = await self._generate_response(
                self.baseline_client,
                self.baseline_model,
                prompt.prompt
            )

            match_result = await self._judge_match(
                prompt,
                candidate_response,
                baseline_response,
                judge_temperature,
                judge_max_tokens
            )

            winner = match_result.get("winner", "tie").lower()
            confidence = match_result.get("confidence", 0.0) or 0.0
            reason = match_result.get("reason", "")
            judge = match_result.get("judge", self.judge_model or "local_heuristic")

            if winner == "candidate":
                candidate_wins += 1
            elif winner == "baseline":
                baseline_wins += 1
            else:
                ties += 1

            match_summaries.append(
                ArenaMatchSummary(
                    prompt=prompt.prompt,
                    winner=winner,
                    confidence=confidence,
                    judge=judge,
                    reason=reason,
                    candidate_response=candidate_response,
                    baseline_response=baseline_response,
                    metadata=prompt.metadata or {},
                )
            )

        total = candidate_wins + baseline_wins + ties
        win_rate = candidate_wins / total if total else 0.0
        loss_rate = baseline_wins / total if total else 0.0
        tie_rate = ties / total if total else 0.0

        metrics = {
            "candidate_model": self.model,
            "baseline_model": self.baseline_model,
            "candidate_wins": candidate_wins,
            "baseline_wins": baseline_wins,
            "ties": ties,
            "num_matches": total,
            "win_rate": win_rate,
            "loss_rate": loss_rate,
            "tie_rate": tie_rate,
        }

        metadata = {
            "arena_mode": "lmarena",
            "judge_model": self.judge_model,
            "matches": [
                {
                    "prompt": summary.prompt[:200],
                    "winner": summary.winner,
                    "confidence": summary.confidence,
                    "reason": summary.reason,
                    "judge": summary.judge,
                }
                for summary in match_summaries[:10]
            ],
        }

        return self._create_result(
            metrics=metrics,
            metadata=metadata,
            duration=None,
            num_samples=total
        )

    async def evaluate_sync(
        self,
        dataset: Sequence[ArenaPrompt],
        **kwargs,
    ) -> EvaluationResult:
        """Synchronous wrapper using asyncio.run under the hood."""
        import asyncio

        return asyncio.run(self.evaluate(dataset=dataset, **kwargs))

    async def _generate_response(
        self,
        client: BaseClient,
        model: str,
        prompt: str,
    ) -> str:
        """Generate a response for the given prompt."""
        messages = [
            ChatMessage(role="system", content="You are a capable assistant."),
            ChatMessage(role="user", content=prompt),
        ]
        response = await client.chat_completion(
            messages=messages,
            model=model,
            temperature=0.7,
            max_tokens=512,
        )
        return response.content.strip()

    async def _judge_match(
        self,
        prompt: ArenaPrompt,
        candidate_response: str,
        baseline_response: str,
        judge_temperature: float,
        judge_max_tokens: int,
    ) -> Dict[str, Any]:
        """Decide the winner using LMArena or a local fallback."""
        if self.arena_client:
            try:
                result = await self.arena_client.submit_match(
                    prompt=prompt,
                    candidate_response=candidate_response,
                    baseline_response=baseline_response,
                    judge_model=self.judge_model,
                    extra_metadata={"stage": "arena_evaluation"},
                )
                result.setdefault("judge", self.judge_model or "lmarena_default")
                return result
            except httpx.HTTPError as exc:
                logger.warning(
                    "Arena API call failed, falling back to local judging",
                    error=str(exc)
                )

        if self.judge_client and self.judge_model:
            judge_prompt = self._format_judge_prompt(
                prompt.prompt,
                candidate_response,
                baseline_response
            )
            messages = [
                ChatMessage(
                    role="system",
                    content="You are an impartial judge. Respond with JSON including keys winner, confidence, and reason."
                ),
                ChatMessage(role="user", content=judge_prompt),
            ]
            response = await self.judge_client.chat_completion(
                messages=messages,
                model=self.judge_model,
                temperature=judge_temperature,
                max_tokens=judge_max_tokens,
            )
            parsed = self._parse_judge_output(response.content)
            parsed.setdefault("judge", self.judge_model)
            return parsed

        return self._heuristic_judge(prompt, candidate_response, baseline_response)

    def _format_judge_prompt(
        self,
        prompt: str,
        candidate_response: str,
        baseline_response: str,
    ) -> str:
        """Create a judge prompt for local model judging."""
        return (
            "Evaluate the following two responses to the same prompt. "
            "Return a JSON object with keys 'winner' (candidate|baseline|tie), "
            "'confidence' (0.0-1.0), and 'reason'.\n\n"
            f"Prompt:\n{prompt}\n\n"
            "Response A (candidate):\n"
            f"{candidate_response}\n\n"
            "Response B (baseline):\n"
            f"{baseline_response}\n"
        )

    def _parse_judge_output(self, content: str) -> Dict[str, Any]:
        """Parse judge model output, defaulting to tie on failure."""
        try:
            return json.loads(content.strip())
        except json.JSONDecodeError:
            lower = content.lower()
            if "candidate" in lower and "baseline" not in lower:
                return {"winner": "candidate", "confidence": 0.5, "reason": content}
            if "baseline" in lower and "candidate" not in lower:
                return {"winner": "baseline", "confidence": 0.5, "reason": content}
            return {"winner": "tie", "confidence": 0.0, "reason": content}

    def _heuristic_judge(
        self,
        prompt: ArenaPrompt,
        candidate_response: str,
        baseline_response: str,
    ) -> Dict[str, Any]:
        """Fallback heuristic judge using reference similarity or length."""
        if prompt.reference:
            candidate_score = SequenceMatcher(
                None, candidate_response.lower(), prompt.reference.lower()
            ).ratio()
            baseline_score = SequenceMatcher(
                None, baseline_response.lower(), prompt.reference.lower()
            ).ratio()
            if abs(candidate_score - baseline_score) < 0.05:
                winner = "tie"
            elif candidate_score > baseline_score:
                winner = "candidate"
            else:
                winner = "baseline"
            confidence = abs(candidate_score - baseline_score)
            reason = (
                f"Reference similarity scores -> candidate={candidate_score:.3f}, "
                f"baseline={baseline_score:.3f}"
            )
        else:
            candidate_len = len(candidate_response)
            baseline_len = len(baseline_response)
            if abs(candidate_len - baseline_len) < 20:
                winner = "tie"
            elif candidate_len > baseline_len:
                winner = "candidate"
            else:
                winner = "baseline"
            confidence = min(abs(candidate_len - baseline_len) / max(candidate_len, 1), 1.0)
            reason = (
                "Used response length heuristic (no reference or judge available)."
            )

        return {
            "winner": winner,
            "confidence": round(confidence, 3),
            "reason": reason,
            "judge": "heuristic",
        }
