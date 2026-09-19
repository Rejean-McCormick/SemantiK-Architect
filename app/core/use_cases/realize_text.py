from __future__ import annotations

import inspect
from collections.abc import Iterable
from time import perf_counter

import structlog

from app.core.domain.exceptions import LexicalResolutionError, RealizationError
from app.core.domain.models import SurfaceResult
from app.core.domain.planning.construction_plan import ConstructionPlan
from app.core.ports.lexical_resolver_port import LexicalResolverPort
from app.core.ports.realizer_port import RealizerPort
from app.shared.observability import get_tracer

logger = structlog.get_logger()
tracer = get_tracer(__name__)


async def _maybe_await(value):
    return await value if inspect.isawaitable(value) else value


class RealizeText:
    """Canonical realization use case: ConstructionPlan -> SurfaceResult."""

    def __init__(
        self,
        realizer: RealizerPort,
        lexical_resolver: LexicalResolverPort | None = None,
    ) -> None:
        if realizer is None or not callable(getattr(realizer, "realize", None)):
            raise TypeError("realizer must implement realize(construction_plan)")
        if lexical_resolver is not None and not callable(
            getattr(lexical_resolver, "resolve_plan", None)
        ):
            raise TypeError("lexical_resolver must implement resolve_plan(construction_plan=...)")
        self.realizer = realizer
        self.lexical_resolver = lexical_resolver

    async def execute(self, construction_plan: ConstructionPlan) -> SurfaceResult:
        if not isinstance(construction_plan, ConstructionPlan):
            raise RealizationError("RealizeText requires a ConstructionPlan.")
        plan = construction_plan.validate()

        with tracer.start_as_current_span("use_case.realize_text") as span:
            span.set_attribute("app.lang_code", plan.lang_code)
            span.set_attribute("app.construction_id", plan.construction_id)
            started = perf_counter()

            try:
                resolved_plan = plan
                if self.lexical_resolver is not None:
                    try:
                        resolved_plan = await _maybe_await(
                            self.lexical_resolver.resolve_plan(construction_plan=plan)
                        )
                    except Exception as exc:
                        if isinstance(exc, LexicalResolutionError):
                            raise
                        raise LexicalResolutionError(str(exc)) from exc
                    if not isinstance(resolved_plan, ConstructionPlan):
                        raise LexicalResolutionError(
                            "Lexical resolver must return a ConstructionPlan."
                        )
                    resolved_plan.validate()

                raw = await _maybe_await(self.realizer.realize(resolved_plan))
                if not isinstance(raw, SurfaceResult):
                    raise RealizationError(
                        "Realizer must return SurfaceResult, got "
                        f"{type(raw).__name__}."
                    )
                if raw.lang_code != resolved_plan.lang_code:
                    raise RealizationError(
                        f"Realizer language mismatch: plan={resolved_plan.lang_code!r}, "
                        f"result={raw.lang_code!r}."
                    )
                if raw.construction_id != resolved_plan.construction_id:
                    raise RealizationError(
                        "Realizer construction mismatch: "
                        f"plan={resolved_plan.construction_id!r}, "
                        f"result={raw.construction_id!r}."
                    )

                elapsed_ms = max((perf_counter() - started) * 1000.0, 0.0)
                debug = dict(raw.debug_info)
                debug.update(
                    {
                        "runtime_path": "planner_first",
                        "lang_code": raw.lang_code,
                        "construction_id": raw.construction_id,
                        "renderer_backend": raw.renderer_backend,
                        "fallback_used": bool(raw.fallback_used),
                        "slot_keys": list(resolved_plan.slot_keys),
                    }
                )
                debug.setdefault("selected_backend", raw.renderer_backend)
                debug.setdefault("attempted_backends", [raw.renderer_backend])

                result = SurfaceResult(
                    text=raw.text,
                    lang_code=raw.lang_code,
                    construction_id=raw.construction_id,
                    renderer_backend=raw.renderer_backend,
                    fallback_used=bool(raw.fallback_used),
                    tokens=list(raw.tokens),
                    debug_info=debug,
                    generation_time_ms=max(float(raw.generation_time_ms), elapsed_ms),
                )
                logger.info(
                    "realization_completed",
                    lang_code=result.lang_code,
                    construction_id=result.construction_id,
                    renderer_backend=result.renderer_backend,
                    fallback_used=result.fallback_used,
                    generation_time_ms=result.generation_time_ms,
                )
                return result
            except (LexicalResolutionError, RealizationError):
                raise
            except Exception as exc:
                logger.error("realization_failed", error=str(exc), exc_info=True)
                raise RealizationError(str(exc)) from exc

    async def execute_many(
        self,
        construction_plans: Iterable[ConstructionPlan],
    ) -> list[SurfaceResult]:
        results: list[SurfaceResult] = []
        for index, plan in enumerate(construction_plans):
            try:
                results.append(await self.execute(plan))
            except RealizationError as exc:
                raise RealizationError(
                    f"Failed to realize sentence at index {index}: {exc}"
                ) from exc
        return results

    __call__ = execute


__all__ = ["RealizeText", "LexicalResolutionError", "RealizationError"]
