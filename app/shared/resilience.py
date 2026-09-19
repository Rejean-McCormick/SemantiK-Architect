from __future__ import annotations

import asyncio
import time
from enum import Enum
from functools import wraps
from typing import Any, Awaitable, Callable, Dict, TypeVar

import structlog

from app.shared.config import settings

logger = structlog.get_logger()
T = TypeVar("T")


class ResilienceError(Exception):
    """Base class for resilience-related failures."""


class CircuitBreakerOpenError(ResilienceError):
    """Raised when a call is blocked because the circuit is open."""

    def __init__(self, service_name: str, reset_timeout: float):
        self.service_name = service_name
        self.reset_timeout = reset_timeout
        super().__init__(
            f"Circuit breaker for {service_name} is open. "
            f"Retry after approximately {reset_timeout}s."
        )


class CircuitState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    """Small in-process circuit breaker for runtime external calls."""

    def __init__(
        self,
        name: str,
        *,
        failure_threshold: int = 5,
        recovery_timeout: float = 30.0,
    ) -> None:
        self.name = name
        self.failure_threshold = max(int(failure_threshold), 1)
        self.recovery_timeout = max(float(recovery_timeout), 0.0)
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = 0.0

    def call(self, func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
        self._check_state()
        try:
            result = func(*args, **kwargs)
        except Exception:
            self._handle_failure()
            raise
        self._handle_success()
        return result

    async def a_call(
        self,
        func: Callable[..., Awaitable[T]],
        *args: Any,
        **kwargs: Any,
    ) -> T:
        self._check_state()
        try:
            result = await func(*args, **kwargs)
        except Exception:
            self._handle_failure()
            raise
        self._handle_success()
        return result

    def _check_state(self) -> None:
        if self.state == CircuitState.OPEN:
            elapsed = time.monotonic() - self.last_failure_time
            if elapsed >= self.recovery_timeout:
                self._transition_to(CircuitState.HALF_OPEN)
            else:
                raise CircuitBreakerOpenError(self.name, self.recovery_timeout - elapsed)

    def _handle_success(self) -> None:
        if self.state == CircuitState.HALF_OPEN or self.failure_count:
            self.failure_count = 0
            self.state = CircuitState.CLOSED

    def _handle_failure(self) -> None:
        self.failure_count += 1
        self.last_failure_time = time.monotonic()
        if self.state == CircuitState.HALF_OPEN or self.failure_count >= self.failure_threshold:
            self._transition_to(CircuitState.OPEN)

    def _transition_to(self, new_state: CircuitState) -> None:
        self.state = new_state
        logger.warning(
            "circuit_breaker_state_change",
            service=self.name,
            state=new_state.value,
            failures=self.failure_count,
        )


_breakers: Dict[str, CircuitBreaker] = {}


def get_circuit_breaker(service_name: str) -> CircuitBreaker:
    breaker = _breakers.get(service_name)
    if breaker is None:
        breaker = CircuitBreaker(
            service_name,
            failure_threshold=5,
            recovery_timeout=float(settings.WIKIDATA_TIMEOUT),
        )
        _breakers[service_name] = breaker
    return breaker


def retry_external_api(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
    """Retry transient external-I/O failures with bounded exponential backoff."""

    @wraps(func)
    async def wrapped(*args: Any, **kwargs: Any) -> T:
        delay = 0.05
        last_exc: BaseException | None = None
        for attempt in range(1, 6):
            try:
                return await func(*args, **kwargs)
            except (IOError, TimeoutError, ConnectionError) as exc:
                last_exc = exc
                if attempt == 5:
                    raise
                logger.warning(
                    "external_api_retry",
                    function=getattr(func, "__name__", "external_call"),
                    attempt=attempt,
                    error=str(exc),
                )
                await asyncio.sleep(delay)
                delay = min(delay * 2.0, 0.5)
        assert last_exc is not None
        raise last_exc

    return wrapped


__all__ = [
    "CircuitBreaker",
    "CircuitBreakerOpenError",
    "CircuitState",
    "ResilienceError",
    "get_circuit_breaker",
    "retry_external_api",
]
