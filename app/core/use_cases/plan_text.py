from __future__ import annotations

import inspect
from collections.abc import Mapping
from typing import Any

import structlog

from app.core.bridges.frame_to_plan import frames_to_plans
from app.core.domain.exceptions import InvalidFrameError, PlanningError
from app.core.domain.planning.planned_sentence import PlannedSentence
from app.core.ports.planner_port import PlannerPort
from app.shared.observability import get_tracer

logger = structlog.get_logger()
tracer = get_tracer(__name__)


class PlanText:
    """Canonical planning use case.

    The default planner is the deterministic frame-to-plan bridge. An injected
    planner must implement the one PlannerPort signature; alternate method names
    and mapping-like planner outputs are not accepted.
    """

    def __init__(self, planner: PlannerPort | None = None) -> None:
        self.planner = planner

    async def execute(self, lang_code: str, frame: Any) -> list[PlannedSentence]:
        lang = self._normalize_lang_code(lang_code)
        self._validate_frame(frame)
        frame_type = self._frame_type(frame)

        with tracer.start_as_current_span("use_case.plan_text") as span:
            span.set_attribute("app.lang_code", lang)
            span.set_attribute("app.frame_type", frame_type)
            logger.info("planning_started", lang=lang, frame_type=frame_type)

            try:
                if self.planner is None:
                    planned = frames_to_plans([frame], lang_code=lang)
                else:
                    raw = self.planner.plan([frame], lang_code=lang, domain="auto")
                    planned = await raw if inspect.isawaitable(raw) else raw

                if not isinstance(planned, list):
                    raise PlanningError("Planner must return list[PlannedSentence].")
                if not planned:
                    raise PlanningError("Planner returned no PlannedSentence objects.")
                if not all(isinstance(item, PlannedSentence) for item in planned):
                    raise PlanningError("Planner returned a non-PlannedSentence item.")

                for item in planned:
                    if item.lang_code != lang:
                        raise PlanningError(
                            f"Planner language mismatch: expected {lang!r}, got {item.lang_code!r}."
                        )

                logger.info(
                    "planning_success",
                    lang=lang,
                    frame_type=frame_type,
                    plan_count=len(planned),
                    construction_ids=[item.construction_id for item in planned],
                )
                return planned
            except (InvalidFrameError, PlanningError):
                raise
            except Exception as exc:
                logger.error("planning_failed", error=str(exc), exc_info=True)
                raise PlanningError(str(exc)) from exc

    async def execute_one(self, lang_code: str, frame: Any) -> PlannedSentence:
        planned = await self.execute(lang_code, frame)
        if len(planned) != 1:
            raise PlanningError(
                f"Single-sentence generation requires exactly one plan; got {len(planned)}."
            )
        return planned[0]

    @staticmethod
    def _normalize_lang_code(value: str) -> str:
        lang = str(value or "").strip().lower().replace("_", "-")
        if not lang:
            raise InvalidFrameError("Language code is required.")
        return lang

    @staticmethod
    def _frame_type(frame: Any) -> str:
        if isinstance(frame, Mapping):
            return str(frame.get("frame_type") or "").strip().lower()
        return str(getattr(frame, "frame_type", "") or "").strip().lower()

    def _validate_frame(self, frame: Any) -> None:
        if frame is None:
            raise InvalidFrameError("Frame is required.")
        frame_type = self._frame_type(frame)
        if not frame_type:
            raise InvalidFrameError("Frame must declare a non-empty frame_type.")
        if frame_type == "bio":
            subject = frame.get("subject") if isinstance(frame, Mapping) else getattr(frame, "subject", None)
            if isinstance(subject, Mapping):
                name = subject.get("name")
            else:
                name = getattr(subject, "name", None)
            if not isinstance(name, str) or not name.strip():
                raise InvalidFrameError("bio frames require subject.name.")


__all__ = ["PlanText"]
