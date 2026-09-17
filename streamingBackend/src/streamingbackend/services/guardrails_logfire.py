"""Logfire instrumentation for NeMo Guardrails."""

from __future__ import annotations

from typing import Any, Optional

import logfire
from langchain_core.runnables import RunnableConfig
from nemoguardrails.integrations.langchain.runnable_rails import RunnableRails
from nemoguardrails.rails.llm.options import (
    ActivatedRail,
    GenerationLogOptions,
    GenerationOptions,
    GenerationResponse,
)

DEFAULT_REFUSE_MESSAGE = "I'm sorry, I can't respond to that."
_PREVIEW_LIMIT = 240


def _truncate(value: object | None, limit: int = _PREVIEW_LIMIT) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return ""
    if len(text) <= limit:
        return text
    return f"{text[: limit - 3]}..."


def _serialize_rail(rail: ActivatedRail) -> dict[str, Any]:
    actions: list[dict[str, Any]] = []
    for action in rail.executed_actions:
        action_info: dict[str, Any] = {
            "name": action.action_name,
            "duration_s": action.duration,
        }
        if action.return_value is not None:
            action_info["return_value"] = action.return_value
        if action.llm_calls:
            action_info["llm_calls"] = [
                {
                    "task": call.task,
                    "duration_s": call.duration,
                    "completion_preview": _truncate(call.completion, 120),
                }
                for call in action.llm_calls
            ]
        actions.append(action_info)

    return {
        "type": rail.type,
        "name": rail.name,
        "stop": rail.stop,
        "decisions": rail.decisions,
        "duration_s": rail.duration,
        "actions": actions,
    }


def _detect_block(
    generation: GenerationResponse,
    *,
    input_blocked_message: str,
    output_blocked_message: str,
) -> tuple[bool, str | None, str | None]:
    """Return (blocked, stage, rail_name)."""
    response_text = generation.response
    if isinstance(response_text, list):
        response_text = response_text[0] if response_text else ""
    response_text = str(response_text or "").strip()

    known_blocked_messages = {
        DEFAULT_REFUSE_MESSAGE,
        input_blocked_message.strip(),
        output_blocked_message.strip(),
    }

    blocked_by_message = response_text in known_blocked_messages

    if generation.log and generation.log.activated_rails:
        for rail in generation.log.activated_rails:
            if not rail.stop:
                continue
            if rail.type in {"input", "output"}:
                return True, rail.type, rail.name

    if blocked_by_message:
        # Fall back to last stopping rail if message matches a refusal template.
        if generation.log and generation.log.activated_rails:
            for rail in reversed(generation.log.activated_rails):
                if rail.stop and rail.type in {"input", "output"}:
                    return True, rail.type, rail.name
        return True, "unknown", None

    return False, None, None


def log_guardrails_generation(
    generation: GenerationResponse,
    *,
    input_blocked_message: str,
    output_blocked_message: str,
    input_type: str | None = None,
) -> dict[str, Any]:
    """Emit structured guardrails telemetry to Logfire."""
    blocked, block_stage, block_rail = _detect_block(
        generation,
        input_blocked_message=input_blocked_message,
        output_blocked_message=output_blocked_message,
    )

    activated_rails: list[dict[str, Any]] = []
    stats: dict[str, Any] = {}
    llm_calls: list[dict[str, Any]] = []

    if generation.log:
        activated_rails = [_serialize_rail(rail) for rail in generation.log.activated_rails]
        if generation.log.stats:
            stats = {
                "total_duration_s": generation.log.stats.total_duration,
                "input_rails_duration_s": generation.log.stats.input_rails_duration,
                "output_rails_duration_s": generation.log.stats.output_rails_duration,
                "llm_calls_count": generation.log.stats.llm_calls_count,
                "llm_calls_total_tokens": generation.log.stats.llm_calls_total_tokens,
            }
        if generation.log.llm_calls:
            llm_calls = [
                {
                    "task": call.task,
                    "model": call.llm_model_name,
                    "duration_s": call.duration,
                    "total_tokens": call.total_tokens,
                    "completion_preview": _truncate(call.completion, 120),
                }
                for call in generation.log.llm_calls
            ]

    response_text = generation.response
    if isinstance(response_text, list):
        response_text = response_text[0] if response_text else ""
    response_text = str(response_text or "")

    payload: dict[str, Any] = {
        "blocked": blocked,
        "block_stage": block_stage,
        "block_rail": block_rail,
        "input_type": input_type,
        "response_preview": _truncate(response_text),
        "activated_rails": activated_rails,
        "stats": stats,
        "llm_calls": llm_calls,
    }

    if blocked:
        logfire.warn("guardrails blocked message", **payload)
    else:
        logfire.info("guardrails passed message", **payload)

    return payload


class LogfireRunnableRails(RunnableRails):
    """RunnableRails that records guardrail decisions to Logfire."""

    def _generation_options(self) -> GenerationOptions:
        return GenerationOptions(
            output_vars=True,
            log=GenerationLogOptions(
                activated_rails=True,
                llm_calls=True,
            ),
        )

    def _full_rails_invoke(
        self,
        input: Any,
        config: Optional[RunnableConfig] = None,
        **kwargs: Any,
    ) -> Any:
        input_messages = self._transform_input_to_rails_format(input)

        with logfire.span("nemoguardrails.generate") as span:
            generation = self.rails.generate(
                messages=input_messages,
                options=self._generation_options(),
            )
            payload = log_guardrails_generation(
                generation,
                input_blocked_message=self.input_blocked_message,
                output_blocked_message=self.output_blocked_message,
                input_type=type(input).__name__,
            )
            span.set_attribute("guardrails.blocked", payload["blocked"])
            if payload["block_stage"]:
                span.set_attribute("guardrails.block_stage", payload["block_stage"])
            if payload["block_rail"]:
                span.set_attribute("guardrails.block_rail", payload["block_rail"])

            context = generation.output_data or {}
            result = generation.response
            if isinstance(result, list) and result:
                result = result[0]

            return self._format_output(
                input,
                result,
                context,
                generation.tool_calls,
                generation.llm_metadata,
            )
