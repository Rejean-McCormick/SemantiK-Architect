from __future__ import annotations

from typing import Any

import structlog

from app.core.bridges.frame_to_slots import frame_to_slots
from app.core.domain.exceptions import InvalidFrameError, LanguageNotFoundError
from app.core.domain.models import SurfaceResult
from app.core.domain.planning.construction_plan import ConstructionPlan
from app.core.ports.language_capabilities_port import LanguageCapabilitiesPort
from app.core.ports.lexical_resolver_port import LexicalResolverPort
from app.core.ports.planner_port import PlannerPort
from app.core.ports.realizer_port import RealizerPort
from app.core.use_cases.plan_text import PlanText
from app.core.use_cases.realize_text import RealizeText
from app.shared.observability import get_tracer

logger = structlog.get_logger()
tracer = get_tracer(__name__)


class GenerateText:
    """Canonical generation facade.

    semantic Frame -> PlannedSentence -> ConstructionPlan -> lexical resolution
    -> realization -> SurfaceResult
    """

    def __init__(
        self,
        *,
        realizer: RealizerPort,
        capabilities: LanguageCapabilitiesPort,
        lexical_resolver: LexicalResolverPort | None = None,
        planner: PlannerPort | None = None,
    ) -> None:
        if realizer is None:
            raise TypeError("realizer is required")
        if capabilities is None:
            raise TypeError("capabilities is required")
        self._planner = PlanText(planner=planner)
        self._realizer = RealizeText(
            realizer=realizer,
            lexical_resolver=lexical_resolver,
        )
        self.capabilities = capabilities

    async def execute(self, lang_code: str, frame: Any) -> SurfaceResult:
        lang = self._normalize_lang_code(lang_code)
        if frame is None:
            raise InvalidFrameError("Frame is required.")
        if not await self.capabilities.supports(lang):
            raise LanguageNotFoundError(lang)

        frame_type = str(getattr(frame, "frame_type", "") or "").strip().lower()
        if not frame_type:
            raise InvalidFrameError("Frame must declare a non-empty frame_type.")

        with tracer.start_as_current_span("use_case.generate_text") as span:
            span.set_attribute("app.lang_code", lang)
            span.set_attribute("app.frame_type", frame_type)
            logger.info("generation_started", lang=lang, frame_type=frame_type)

            planned = await self._planner.execute_one(lang, frame)
            source_frame = planned.frame if planned.frame is not None else frame
            slot_map = frame_to_slots(
                source_frame,
                construction_id=planned.construction_id,
            )
            plan = ConstructionPlan(
                construction_id=planned.construction_id,
                lang_code=planned.lang_code,
                slot_map=slot_map,
                generation_options=dict(planned.generation_options),
                topic_entity_id=planned.topic_entity_id,
                focus_role=planned.focus_role,
                metadata=dict(planned.metadata),
            )

            result = await self._realizer.execute(plan)
            span.set_attribute("app.construction_id", result.construction_id)
            span.set_attribute("app.renderer_backend", result.renderer_backend)
            span.set_attribute("app.fallback_used", result.fallback_used)
            logger.info(
                "generation_success",
                lang=result.lang_code,
                construction_id=result.construction_id,
                renderer_backend=result.renderer_backend,
                fallback_used=result.fallback_used,
                runtime_path="planner_first",
                text_preview=result.text[:80],
            )
            return result

    @staticmethod
    def _normalize_lang_code(value: str) -> str:
        lang = str(value or "").strip().lower().replace("_", "-")
        if not lang:
            raise InvalidFrameError("Language code is required.")
        return lang


__all__ = ["GenerateText"]
