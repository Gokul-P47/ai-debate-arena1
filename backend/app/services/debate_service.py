"""Talk-show orchestration: Host + N guests (2–4) with overlapped TTS."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from app.agents.guest_agent import GuestAgent
from app.agents.host_agent import HOST_SPEAKER_NAME, HostAgent
from app.core.config import Settings, get_settings
from app.core.participants import GuestSpec, guest_public_meta, guests_for_count
from app.providers.base_provider import BaseProvider
from app.providers.factory import get_provider
from app.schemas.debate_request import DebateRequest
from app.schemas.debate_response import (
    DebateMessage,
    DebateMetadata,
    DebateResponse,
    DebateTurn,
    SpeakerRole,
)
from app.schemas.roles import HostSegment
from app.services.agent_context import AgentPrompt
from app.services.claim_extractor import ClaimExtractor
from app.services.context_builder import ContextBuilder
from app.services.contradiction_analyzer import ContradictionAnalyzer
from app.services.memory_service import MemoryService
from app.services.tts_service import ElevenLabsTTSService
from app.utils.logger import get_logger

logger = get_logger(__name__)


class DebateService:
    """Host + configurable guests with claim memory and overlapped TTS."""

    def __init__(
        self,
        provider: BaseProvider | None = None,
        tts: ElevenLabsTTSService | None = None,
    ) -> None:
        self._provider = provider
        self._tts = tts

    def _resolve_provider(self) -> BaseProvider:
        return self._provider or get_provider()

    def _resolve_tts(self) -> ElevenLabsTTSService:
        return self._tts or ElevenLabsTTSService()

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
        if role == SpeakerRole.HOST:
            return

        extracted = await extractor.extract(response_text=response_text, topic=topic)
        memory.append_claims(role, extracted, round_number=round_number)

        peer_roles = memory.other_guest_roles(role)
        analysis = await analyzer.analyze(
            response_text=response_text,
            topic=topic,
            target_claims=memory.open_claims_for_roles(peer_roles),
            own_claims=memory.memory_for(role).open_claims(),
        )

        # Claim ids are unique globally; find owner among peers for each contradiction.
        peer_claim_owner: dict[str, SpeakerRole] = {}
        for peer in peer_roles:
            for claim in memory.memory_for(peer).claims:
                peer_claim_owner[claim.id] = peer

        for link in analysis.contradictions:
            owner = peer_claim_owner.get(link.claim_id)
            if owner is None:
                continue
            memory.mark_contradicted(
                owner,
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
        try:
            await self._ingest_response(**kwargs)
            return None
        except Exception as exc:  # noqa: BLE001
            logger.exception("Claim ingest failed: %s", exc)
            return str(exc)

    async def _make_audio_event(
        self,
        *,
        tts: ElevenLabsTTSService,
        message: DebateMessage,
        language: str,
    ) -> dict[str, Any] | None:
        if not tts.enabled:
            return None
        try:
            speech = await tts.synthesize(
                text=message.content,
                role=message.role,
                language=language,
            )
            if speech is None:
                return None
            return {
                "event": "audio_ready",
                "data": {
                    "role": message.role.value,
                    "speaker": message.speaker,
                    "roundNumber": message.round_number,
                    "audioId": speech.audio_id,
                    "audioUrl": f"/api/v1/audio/{speech.audio_id}",
                    "mimeType": speech.mime_type,
                },
            }
        except Exception as exc:  # noqa: BLE001
            logger.exception("TTS failed for %s: %s", message.role.value, exc)
            return {
                "event": "status",
                "data": {"message": f"TTS skipped: {exc}"},
            }

    async def _stream_turn(
        self,
        *,
        agent: HostAgent | GuestAgent,
        prompt: AgentPrompt,
        speaker: str,
        role: SpeakerRole,
        round_number: int,
        memory: MemoryService,
    ) -> AsyncIterator[dict[str, Any]]:
        yield {
            "event": "turn_started",
            "data": {
                "role": role.value,
                "speaker": speaker,
                "roundNumber": round_number,
            },
        }

        parts: list[str] = []
        async for chunk in agent.stream(prompt):
            parts.append(chunk)
            yield {
                "event": "token",
                "data": {
                    "role": role.value,
                    "roundNumber": round_number,
                    "delta": chunk,
                },
            }

        message = agent.finalize("".join(parts), round_number)
        memory.add_message(message)
        yield {
            "event": "message_completed",
            "data": {"message": message.model_dump(by_alias=True, mode="json")},
        }

    async def _interleave_tts_with_turn(
        self,
        pending_tts: asyncio.Task[dict[str, Any] | None] | None,
        turn: AsyncIterator[dict[str, Any]],
    ) -> AsyncIterator[dict[str, Any]]:
        async def _next_or_none() -> dict[str, Any] | None:
            try:
                return await anext(aiter)
            except StopAsyncIteration:
                return None

        aiter = turn.__aiter__()
        turn_task: asyncio.Task[dict[str, Any] | None] | None = asyncio.create_task(
            _next_or_none()
        )
        tts_task = pending_tts

        while turn_task is not None:
            wait_for: set[asyncio.Task[Any]] = {turn_task}
            if tts_task is not None:
                wait_for.add(tts_task)

            done, _ = await asyncio.wait(wait_for, return_when=asyncio.FIRST_COMPLETED)

            if tts_task is not None and tts_task in done:
                event = tts_task.result()
                tts_task = None
                if event is not None:
                    yield event

            if turn_task in done:
                event = turn_task.result()
                if event is None:
                    turn_task = None
                    break
                yield event
                turn_task = asyncio.create_task(_next_or_none())

        if tts_task is not None:
            event = await tts_task
            if event is not None:
                yield event

    async def _flush_tts(
        self,
        pending_tts: asyncio.Task[dict[str, Any] | None] | None,
    ) -> AsyncIterator[dict[str, Any]]:
        if pending_tts is None:
            return
        event = await pending_tts
        if event is not None:
            yield event

    def _start_tts(
        self,
        *,
        tts: ElevenLabsTTSService,
        message: DebateMessage,
        language: str,
    ) -> asyncio.Task[dict[str, Any] | None] | None:
        if not tts.enabled:
            return None
        return asyncio.create_task(
            self._make_audio_event(tts=tts, message=message, language=language)
        )

    def _guest_agents(
        self, provider: BaseProvider, guests: list[GuestSpec]
    ) -> dict[SpeakerRole, GuestAgent]:
        return {
            g.role: GuestAgent(provider, role=g.role, speaker_name=g.name)
            for g in guests
        }

    async def stream_debate(self, request: DebateRequest) -> AsyncIterator[dict[str, Any]]:
        settings = get_settings()
        try:
            provider = self._resolve_provider()
        except Exception as exc:  # noqa: BLE001
            yield {"event": "error", "data": {"message": str(exc)}}
            return

        guests = guests_for_count(request.participant_count)
        host_agent = HostAgent(provider)
        guest_agents = self._guest_agents(provider, guests)
        extractor = ClaimExtractor(provider)
        analyzer = ContradictionAnalyzer(provider)
        tts = self._resolve_tts()

        from app.utils.news import fetch_latest_news
        news_articles = await fetch_latest_news(request.topic)

        debate_id = str(uuid4())
        created_at = datetime.now(timezone.utc)
        memory = MemoryService(
            debate_id=debate_id,
            topic=request.topic,
            language=request.language,
            mood=request.mood.value,
            guests=guests,
            news_articles=news_articles,
        )
        context_builder = ContextBuilder(memory)
        pending_tts: asyncio.Task[dict[str, Any] | None] | None = None
        participants_meta = guest_public_meta(len(guests))

        yield {
            "event": "debate_started",
            "data": {
                "debateId": debate_id,
                "topic": request.topic,
                "language": request.language,
                "mood": request.mood.value,
                "rounds": request.rounds,
                "turnSeconds": request.turn_seconds,
                "participantCount": len(guests),
                "participants": participants_meta,
                "provider": settings.llm_provider,
                "model": self._model_for_provider(settings),
                "ttsEnabled": tts.enabled,
                "newsArticles": news_articles,
            },
        }

        logger.info(
            "Streaming talk show %s — topic=%r guests=%d rounds=%d",
            debate_id,
            request.topic,
            len(guests),
            request.rounds,
        )

        try:
            opening = context_builder.build_host_prompt(
                topic=request.topic,
                mood=request.mood,
                language=request.language,
                round_number=1,
                total_rounds=request.rounds,
                turn_seconds=request.turn_seconds,
                segment=HostSegment.OPENING,
            )
            async for event in self._stream_turn(
                agent=host_agent,
                prompt=opening,
                speaker=HOST_SPEAKER_NAME,
                role=SpeakerRole.HOST,
                round_number=1,
                memory=memory,
            ):
                yield event
            pending_tts = self._start_tts(
                tts=tts,
                message=memory.messages[-1],
                language=request.language,
            )

            for round_number in range(1, request.rounds + 1):
                round_prompt = context_builder.build_host_prompt(
                    topic=request.topic,
                    mood=request.mood,
                    language=request.language,
                    round_number=round_number,
                    total_rounds=request.rounds,
                    turn_seconds=request.turn_seconds,
                    segment=HostSegment.ROUND,
                )
                async for event in self._interleave_tts_with_turn(
                    pending_tts,
                    self._stream_turn(
                        agent=host_agent,
                        prompt=round_prompt,
                        speaker=HOST_SPEAKER_NAME,
                        role=SpeakerRole.HOST,
                        round_number=round_number,
                        memory=memory,
                    ),
                ):
                    yield event
                pending_tts = self._start_tts(
                    tts=tts,
                    message=memory.messages[-1],
                    language=request.language,
                )

                round_messages: list[DebateMessage] = []
                peer_latest: str | None = None

                for guest in guests:
                    agent = guest_agents[guest.role]
                    prompt = context_builder.build_guest_prompt(
                        guest=guest,
                        topic=request.topic,
                        mood=request.mood,
                        language=request.language,
                        round_number=round_number,
                        total_rounds=request.rounds,
                        turn_seconds=request.turn_seconds,
                        peer_latest=peer_latest,
                    )
                    async for event in self._interleave_tts_with_turn(
                        pending_tts,
                        self._stream_turn(
                            agent=agent,
                            prompt=prompt,
                            speaker=guest.name,
                            role=guest.role,
                            round_number=round_number,
                            memory=memory,
                        ),
                    ):
                        yield event

                    guest_message = memory.messages[-1]
                    round_messages.append(guest_message)
                    peer_latest = guest_message.content

                    yield {
                        "event": "status",
                        "data": {"message": f"Updating {guest.name}'s claim memory…"},
                    }
                    ingest_error = await self._safe_ingest(
                        memory=memory,
                        extractor=extractor,
                        analyzer=analyzer,
                        role=guest.role,
                        response_text=guest_message.content,
                        topic=request.topic,
                        round_number=round_number,
                    )
                    if ingest_error:
                        yield {
                            "event": "status",
                            "data": {"message": f"Claim update skipped: {ingest_error}"},
                        }

                    pending_tts = self._start_tts(
                        tts=tts,
                        message=guest_message,
                        language=request.language,
                    )

                support_msg = next(
                    (m for m in round_messages if m.role == SpeakerRole.SUPPORT),
                    round_messages[0] if round_messages else None,
                )
                opposition_msg = next(
                    (m for m in round_messages if m.role == SpeakerRole.OPPOSITION),
                    round_messages[1] if len(round_messages) > 1 else support_msg,
                )
                memory.add_turn(
                    DebateTurn(
                        round_number=round_number,
                        messages=round_messages,
                        support=support_msg,
                        opposition=opposition_msg,
                    )
                )

            closing = context_builder.build_host_prompt(
                topic=request.topic,
                mood=request.mood,
                language=request.language,
                round_number=request.rounds,
                total_rounds=request.rounds,
                turn_seconds=request.turn_seconds,
                segment=HostSegment.CLOSING,
            )
            async for event in self._interleave_tts_with_turn(
                pending_tts,
                self._stream_turn(
                    agent=host_agent,
                    prompt=closing,
                    speaker=HOST_SPEAKER_NAME,
                    role=SpeakerRole.HOST,
                    round_number=request.rounds,
                    memory=memory,
                ),
            ):
                yield event

            pending_tts = self._start_tts(
                tts=tts,
                message=memory.messages[-1],
                language=request.language,
            )
            async for event in self._flush_tts(pending_tts):
                yield event

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
                    "hosted": True,
                    "talkShow": True,
                    "participantCount": len(guests),
                    "participants": participants_meta,
                    "turnSeconds": request.turn_seconds,
                    "ttsEnabled": tts.enabled,
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
                    "participantCount": len(guests),
                    "participants": participants_meta,
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
            if pending_tts is not None and not pending_tts.done():
                pending_tts.cancel()
            yield {"event": "error", "data": {"message": str(exc)}}

    async def create_debate(self, request: DebateRequest) -> DebateResponse:
        settings = get_settings()
        provider = self._resolve_provider()
        guests = guests_for_count(request.participant_count)
        host_agent = HostAgent(provider)
        guest_agents = self._guest_agents(provider, guests)
        extractor = ClaimExtractor(provider)
        analyzer = ContradictionAnalyzer(provider)

        debate_id = str(uuid4())
        created_at = datetime.now(timezone.utc)
        memory = MemoryService(
            debate_id=debate_id,
            topic=request.topic,
            language=request.language,
            mood=request.mood.value,
            guests=guests,
        )
        context_builder = ContextBuilder(memory)

        opening = context_builder.build_host_prompt(
            topic=request.topic,
            mood=request.mood,
            language=request.language,
            round_number=1,
            total_rounds=request.rounds,
            turn_seconds=request.turn_seconds,
            segment=HostSegment.OPENING,
        )
        memory.add_message(await host_agent.generate(opening))

        for round_number in range(1, request.rounds + 1):
            round_prompt = context_builder.build_host_prompt(
                topic=request.topic,
                mood=request.mood,
                language=request.language,
                round_number=round_number,
                total_rounds=request.rounds,
                turn_seconds=request.turn_seconds,
                segment=HostSegment.ROUND,
            )
            memory.add_message(await host_agent.generate(round_prompt))

            round_messages: list[DebateMessage] = []
            peer_latest: str | None = None
            for guest in guests:
                prompt = context_builder.build_guest_prompt(
                    guest=guest,
                    topic=request.topic,
                    mood=request.mood,
                    language=request.language,
                    round_number=round_number,
                    total_rounds=request.rounds,
                    turn_seconds=request.turn_seconds,
                    peer_latest=peer_latest,
                )
                message = await guest_agents[guest.role].generate(prompt)
                memory.add_message(message)
                round_messages.append(message)
                peer_latest = message.content
                await self._ingest_response(
                    memory=memory,
                    extractor=extractor,
                    analyzer=analyzer,
                    role=guest.role,
                    response_text=message.content,
                    topic=request.topic,
                    round_number=round_number,
                )

            support_msg = next(
                (m for m in round_messages if m.role == SpeakerRole.SUPPORT),
                round_messages[0],
            )
            opposition_msg = next(
                (m for m in round_messages if m.role == SpeakerRole.OPPOSITION),
                round_messages[min(1, len(round_messages) - 1)],
            )
            memory.add_turn(
                DebateTurn(
                    round_number=round_number,
                    messages=round_messages,
                    support=support_msg,
                    opposition=opposition_msg,
                )
            )

        closing = context_builder.build_host_prompt(
            topic=request.topic,
            mood=request.mood,
            language=request.language,
            round_number=request.rounds,
            total_rounds=request.rounds,
            turn_seconds=request.turn_seconds,
            segment=HostSegment.CLOSING,
        )
        memory.add_message(await host_agent.generate(closing))

        completed_at = datetime.now(timezone.utc)
        snapshot = memory.snapshot()
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
                    "hosted": True,
                    "talkShow": True,
                    "participantCount": len(guests),
                    "participants": guest_public_meta(len(guests)),
                    "turnSeconds": request.turn_seconds,
                },
            ),
        )
