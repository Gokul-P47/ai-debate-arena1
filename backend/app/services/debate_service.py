"""Debate orchestration service with structured claim memory and streaming."""

from collections.abc import AsyncIterator
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from app.agents.opposition_agent import OPPOSITION_SPEAKER_NAME, OppositionAgent
from app.agents.support_agent import SUPPORT_SPEAKER_NAME, SupportAgent
from app.core.config import Settings, get_settings
from app.providers.base_provider import BaseProvider
from app.providers.factory import get_provider
from app.schemas.debate_request import DebateRequest
from app.schemas.debate_response import (
    DebateMetadata,
    DebateResponse,
    DebateTurn,
    SpeakerRole,
)
from app.services.claim_extractor import ClaimExtractor
from app.services.context_builder import ContextBuilder
from app.services.contradiction_analyzer import ContradictionAnalyzer
from app.services.memory_service import MemoryService
from app.utils.logger import get_logger

logger = get_logger(__name__)


class DebateService:
    """Coordinates multi-round debates using claim-based memory.

    Supports both blocking ``create_debate`` and token-streaming
    ``stream_debate`` for live UI updates.
    """

    def __init__(self, provider: BaseProvider | None = None) -> None:
        self._provider = provider

    def _resolve_provider(self) -> BaseProvider:
        return self._provider or get_provider()

    @staticmethod
    def _model_for_provider(settings: Settings) -> str:
        if settings.llm_provider == "openai":
            return settings.openai_model
        if settings.llm_provider == "grok":
            return settings.grok_model
        return settings.gemini_model

    async def _ingest_response(
        self,
        *,
        memory: MemoryService,
        extractor: ClaimExtractor,
        analyzer: ContradictionAnalyzer,
        role: SpeakerRole,
        response_text: str,
        topic: str,
        round_number: int,
    ) -> None:
        """Extract claims and update contradiction/defense statuses."""
        extracted = await extractor.extract(response_text=response_text, topic=topic)
        memory.append_claims(
            role,
            extracted,
            round_number=round_number,
        )

        opponent_role = (
            SpeakerRole.OPPOSITION
            if role == SpeakerRole.SUPPORT
            else SpeakerRole.SUPPORT
        )
        analysis = await analyzer.analyze(
            response_text=response_text,
            topic=topic,
            target_claims=memory.memory_for(opponent_role).open_claims(),
            own_claims=memory.memory_for(role).open_claims(),
        )

        for link in analysis.contradictions:
            memory.mark_contradicted(
                opponent_role,
                claim_id=link.claim_id,
                statement=link.reason,
            )
        for link in analysis.defenses:
            memory.mark_defended(
                role,
                claim_id=link.claim_id,
                statement=link.reason,
            )

    async def _safe_ingest(self, **kwargs: Any) -> str | None:
        """Run claim ingest; return an error message instead of raising."""
        try:
            await self._ingest_response(**kwargs)
            return None
        except Exception as exc:  # noqa: BLE001 — stream should continue when possible
            logger.exception("Claim ingest failed: %s", exc)
            return str(exc)

    async def stream_debate(self, request: DebateRequest) -> AsyncIterator[dict[str, Any]]:
        """Yield SSE-ready event payloads while tokens are generated.

        Event types:
        - debate_started
        - turn_started
        - token
        - message_completed
        - status
        - debate_completed
        - error
        """
        settings = get_settings()
        try:
            provider = self._resolve_provider()
        except Exception as exc:  # noqa: BLE001
            yield {"event": "error", "data": {"message": str(exc)}}
            return

        support_agent = SupportAgent(provider)
        opposition_agent = OppositionAgent(provider)
        extractor = ClaimExtractor(provider)
        analyzer = ContradictionAnalyzer(provider)

        debate_id = str(uuid4())
        created_at = datetime.now(timezone.utc)
        memory = MemoryService(
            debate_id=debate_id,
            topic=request.topic,
            language=request.language,
            mood=request.mood.value,
        )
        context_builder = ContextBuilder(memory)

        yield {
            "event": "debate_started",
            "data": {
                "debateId": debate_id,
                "topic": request.topic,
                "language": request.language,
                "mood": request.mood.value,
                "rounds": request.rounds,
                "provider": settings.llm_provider,
                "model": self._model_for_provider(settings),
            },
        }

        logger.info(
            "Streaming debate %s — topic=%r rounds=%d mood=%s provider=%s",
            debate_id,
            request.topic,
            request.rounds,
            request.mood.value,
            settings.llm_provider,
        )

        try:
            for round_number in range(1, request.rounds + 1):
                # ── Support ──────────────────────────────────────────────
                support_prompt = context_builder.build_support_prompt(
                    topic=request.topic,
                    mood=request.mood,
                    language=request.language,
                    round_number=round_number,
                    total_rounds=request.rounds,
                )
                yield {
                    "event": "turn_started",
                    "data": {
                        "role": SpeakerRole.SUPPORT.value,
                        "speaker": SUPPORT_SPEAKER_NAME,
                        "roundNumber": round_number,
                    },
                }

                support_parts: list[str] = []
                async for chunk in support_agent.stream(support_prompt):
                    support_parts.append(chunk)
                    yield {
                        "event": "token",
                        "data": {
                            "role": SpeakerRole.SUPPORT.value,
                            "roundNumber": round_number,
                            "delta": chunk,
                        },
                    }

                support_message = support_agent.finalize(
                    "".join(support_parts),
                    round_number,
                )
                memory.add_message(support_message)
                yield {
                    "event": "message_completed",
                    "data": {
                        "message": support_message.model_dump(
                            by_alias=True,
                            mode="json",
                        )
                    },
                }

                yield {
                    "event": "status",
                    "data": {"message": "Updating support claim memory…"},
                }
                ingest_error = await self._safe_ingest(
                    memory=memory,
                    extractor=extractor,
                    analyzer=analyzer,
                    role=SpeakerRole.SUPPORT,
                    response_text=support_message.content,
                    topic=request.topic,
                    round_number=round_number,
                )
                if ingest_error:
                    yield {
                        "event": "status",
                        "data": {
                            "message": f"Claim update skipped: {ingest_error}",
                        },
                    }

                # ── Opposition ───────────────────────────────────────────
                opposition_prompt = context_builder.build_opposition_prompt(
                    topic=request.topic,
                    mood=request.mood,
                    language=request.language,
                    round_number=round_number,
                    total_rounds=request.rounds,
                    opponent_latest=support_message.content,
                )
                yield {
                    "event": "turn_started",
                    "data": {
                        "role": SpeakerRole.OPPOSITION.value,
                        "speaker": OPPOSITION_SPEAKER_NAME,
                        "roundNumber": round_number,
                    },
                }

                opposition_parts: list[str] = []
                async for chunk in opposition_agent.stream(opposition_prompt):
                    opposition_parts.append(chunk)
                    yield {
                        "event": "token",
                        "data": {
                            "role": SpeakerRole.OPPOSITION.value,
                            "roundNumber": round_number,
                            "delta": chunk,
                        },
                    }

                opposition_message = opposition_agent.finalize(
                    "".join(opposition_parts),
                    round_number,
                )
                memory.add_message(opposition_message)
                yield {
                    "event": "message_completed",
                    "data": {
                        "message": opposition_message.model_dump(
                            by_alias=True,
                            mode="json",
                        )
                    },
                }

                yield {
                    "event": "status",
                    "data": {"message": "Updating opposition claim memory…"},
                }
                ingest_error = await self._safe_ingest(
                    memory=memory,
                    extractor=extractor,
                    analyzer=analyzer,
                    role=SpeakerRole.OPPOSITION,
                    response_text=opposition_message.content,
                    topic=request.topic,
                    round_number=round_number,
                )
                if ingest_error:
                    yield {
                        "event": "status",
                        "data": {
                            "message": f"Claim update skipped: {ingest_error}",
                        },
                    }

                memory.add_turn(
                    DebateTurn(
                        round_number=round_number,
                        support=support_message,
                        opposition=opposition_message,
                    )
                )

            completed_at = datetime.now(timezone.utc)
            snapshot = memory.snapshot()
            metadata = DebateMetadata(
                provider=settings.llm_provider,
                model=self._model_for_provider(settings),
                total_rounds=request.rounds,
                created_at=created_at,
                completed_at=completed_at,
                extra={
                    "memoryMode": "structured_claims",
                    "streamed": True,
                    "supportClaimCount": len(snapshot.support_memory.claims),
                    "oppositionClaimCount": len(snapshot.opposition_memory.claims),
                },
            )
            summary = memory.to_debate_summary()
            yield {
                "event": "debate_completed",
                "data": {
                    "debateId": debate_id,
                    "topic": request.topic,
                    "language": request.language,
                    "mood": request.mood.value,
                    "currentRound": request.rounds,
                    "summary": summary.model_dump(by_alias=True, mode="json"),
                    "claimMemory": snapshot.model_dump(by_alias=True, mode="json"),
                    "metadata": metadata.model_dump(by_alias=True, mode="json"),
                    "transcript": [
                        m.model_dump(by_alias=True, mode="json") for m in memory.messages
                    ],
                },
            }
        except Exception as exc:  # noqa: BLE001
            logger.exception("Streaming debate failed: %s", exc)
            yield {"event": "error", "data": {"message": str(exc)}}

    async def create_debate(self, request: DebateRequest) -> DebateResponse:
        """Run a full multi-round debate (blocking) with structured claim tracking."""
        settings = get_settings()
        provider = self._resolve_provider()
        support_agent = SupportAgent(provider)
        opposition_agent = OppositionAgent(provider)
        extractor = ClaimExtractor(provider)
        analyzer = ContradictionAnalyzer(provider)

        debate_id = str(uuid4())
        created_at = datetime.now(timezone.utc)

        memory = MemoryService(
            debate_id=debate_id,
            topic=request.topic,
            language=request.language,
            mood=request.mood.value,
        )
        context_builder = ContextBuilder(memory)

        logger.info(
            "Starting debate %s — topic=%r rounds=%d mood=%s provider=%s",
            debate_id,
            request.topic,
            request.rounds,
            request.mood.value,
            settings.llm_provider,
        )

        for round_number in range(1, request.rounds + 1):
            support_prompt = context_builder.build_support_prompt(
                topic=request.topic,
                mood=request.mood,
                language=request.language,
                round_number=round_number,
                total_rounds=request.rounds,
            )
            support_message = await support_agent.generate(support_prompt)
            memory.add_message(support_message)
            await self._ingest_response(
                memory=memory,
                extractor=extractor,
                analyzer=analyzer,
                role=SpeakerRole.SUPPORT,
                response_text=support_message.content,
                topic=request.topic,
                round_number=round_number,
            )

            opposition_prompt = context_builder.build_opposition_prompt(
                topic=request.topic,
                mood=request.mood,
                language=request.language,
                round_number=round_number,
                total_rounds=request.rounds,
                opponent_latest=support_message.content,
            )
            opposition_message = await opposition_agent.generate(opposition_prompt)
            memory.add_message(opposition_message)
            await self._ingest_response(
                memory=memory,
                extractor=extractor,
                analyzer=analyzer,
                role=SpeakerRole.OPPOSITION,
                response_text=opposition_message.content,
                topic=request.topic,
                round_number=round_number,
            )

            memory.add_turn(
                DebateTurn(
                    round_number=round_number,
                    support=support_message,
                    opposition=opposition_message,
                )
            )

        completed_at = datetime.now(timezone.utc)
        snapshot = memory.snapshot()
        logger.info(
            "Debate %s completed — %d messages, %d support claims, %d opposition claims",
            debate_id,
            memory.message_count,
            len(snapshot.support_memory.claims),
            len(snapshot.opposition_memory.claims),
        )

        return DebateResponse(
            debate_id=debate_id,
            topic=request.topic,
            language=request.language,
            mood=request.mood.value,
            current_round=request.rounds,
            transcript=memory.messages,
            turns=memory.turns,
            summary=memory.to_debate_summary(),
            claim_memory=snapshot,
            metadata=DebateMetadata(
                provider=settings.llm_provider,
                model=self._model_for_provider(settings),
                total_rounds=request.rounds,
                created_at=created_at,
                completed_at=completed_at,
                extra={
                    "memoryMode": "structured_claims",
                    "supportClaimCount": len(snapshot.support_memory.claims),
                    "oppositionClaimCount": len(snapshot.opposition_memory.claims),
                },
            ),
        )
