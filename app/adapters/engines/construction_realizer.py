from __future__ import annotations

import inspect
from typing import Any, Sequence

from app.core.domain.exceptions import DomainError, RealizationError
from app.core.domain.models import SurfaceResult
from app.core.domain.planning.construction_plan import ConstructionPlan
from app.core.ports.realizer_port import RealizerPort, RealizerSupportStatus

_CANONICAL_BACKEND_ORDER = ("gf", "family", "safe_mode")
_ATTEMPTABLE = {"full", "partial", "fallback_only"}


async def _maybe_await(value: Any) -> Any:
    return await value if inspect.isawaitable(value) else value


class ConstructionRealizer:
    """Canonical renderer dispatcher with explicit GF -> family -> safe_mode fallback."""

    def __init__(
        self,
        *,
        gf_realizer: RealizerPort | None = None,
        family_realizer: RealizerPort | None = None,
        safe_mode_realizer: RealizerPort | None = None,
        default_allow_fallback: bool = True,
        dispatch_order: Sequence[str] = _CANONICAL_BACKEND_ORDER,
    ) -> None:
        self._realizers = {
            "gf": gf_realizer,
            "family": family_realizer,
            "safe_mode": safe_mode_realizer,
        }
        order = [name for name in dispatch_order if name in _CANONICAL_BACKEND_ORDER]
        self.dispatch_order = tuple(dict.fromkeys(order + list(_CANONICAL_BACKEND_ORDER)))
        self.default_allow_fallback = bool(default_allow_fallback)

    @property
    def backend_name(self) -> str:
        return "dispatcher"

    def supports(self, construction_id: str, lang_code: str) -> bool:
        return self.get_support_status(construction_id, lang_code) != "unsupported"

    def get_support_status(self, construction_id: str, lang_code: str) -> RealizerSupportStatus:
        statuses = [
            self._support_status(name, self._realizers.get(name), construction_id, lang_code)
            for name in self.dispatch_order
            if self._realizers.get(name) is not None
        ]
        if "full" in statuses:
            return "full"
        if "partial" in statuses:
            return "partial"
        if "fallback_only" in statuses:
            return "fallback_only"
        return "unsupported"

    async def realize(self, construction_plan: ConstructionPlan) -> SurfaceResult:
        if not isinstance(construction_plan, ConstructionPlan):
            raise RealizationError("ConstructionRealizer requires a ConstructionPlan.")
        plan = construction_plan.validate()
        allow_fallback = bool(plan.generation_options.get("allow_fallback", self.default_allow_fallback))

        attempted: list[str] = []
        trace: list[dict[str, str]] = []
        failures: list[str] = []

        for backend_name in self.dispatch_order:
            if backend_name == "safe_mode" and not allow_fallback:
                continue
            realizer = self._realizers.get(backend_name)
            if realizer is None:
                continue
            status = self._support_status(
                backend_name, realizer, plan.construction_id, plan.lang_code
            )
            if status not in _ATTEMPTABLE:
                trace.append({"backend": backend_name, "event": "unsupported"})
                continue
            attempted.append(backend_name)
            try:
                raw = await _maybe_await(realizer.realize(plan))
                if not isinstance(raw, SurfaceResult):
                    raise RealizationError(
                        f"Backend '{backend_name}' returned {type(raw).__name__}, expected SurfaceResult."
                    )
                if raw.construction_id != plan.construction_id:
                    raise RealizationError(
                        f"Backend '{backend_name}' changed construction_id."
                    )
                if raw.lang_code != plan.lang_code:
                    raise RealizationError(f"Backend '{backend_name}' changed lang_code.")

                fallback_used = bool(raw.fallback_used or len(attempted) > 1 or status == "fallback_only")
                debug = dict(raw.debug_info)
                debug.update(
                    {
                        "runtime_path": "planner_first",
                        "construction_id": plan.construction_id,
                        "lang_code": plan.lang_code,
                        "renderer_backend": backend_name,
                        "selected_backend": backend_name,
                        "attempted_backends": list(attempted),
                        "fallback_used": fallback_used,
                        "slot_keys": list(plan.slot_keys),
                        "backend_trace": trace + [{"backend": backend_name, "event": "selected"}],
                    }
                )
                return SurfaceResult(
                    text=raw.text,
                    lang_code=raw.lang_code,
                    construction_id=raw.construction_id,
                    renderer_backend=backend_name,
                    fallback_used=fallback_used,
                    tokens=list(raw.tokens),
                    debug_info=debug,
                    generation_time_ms=raw.generation_time_ms,
                )
            except DomainError as exc:
                failures.append(f"{backend_name}: {exc}")
                trace.append({"backend": backend_name, "event": "failed", "error": str(exc)})
            except Exception as exc:
                failures.append(f"{backend_name}: {exc}")
                trace.append({"backend": backend_name, "event": "failed", "error": str(exc)})

        detail = "; ".join(failures) if failures else "no backend supports the plan"
        raise RealizationError(
            f"Could not realize construction '{plan.construction_id}' for language "
            f"'{plan.lang_code}': {detail}"
        )

    @staticmethod
    def _support_status(
        backend_name: str,
        realizer: Any,
        construction_id: str,
        lang_code: str,
    ) -> RealizerSupportStatus:
        getter = getattr(realizer, "get_support_status", None)
        if callable(getter):
            value = str(getter(construction_id, lang_code)).strip().lower()
            if value in {"full", "partial", "fallback_only", "unsupported"}:
                return value  # type: ignore[return-value]
        supports = getattr(realizer, "supports", None)
        if callable(supports):
            return "full" if supports(construction_id, lang_code) else "unsupported"
        return "fallback_only" if backend_name == "safe_mode" else "unsupported"


__all__ = ["ConstructionRealizer"]
