from __future__ import annotations


class DomainError(Exception):
    """Base class for SemantiK runtime/domain failures."""


class InvalidFrameError(DomainError):
    """Raised when semantic input violates the canonical frame contract."""

    def __init__(self, reason: str):
        super().__init__(f"Invalid Semantic Frame: {reason}")


class UnsupportedFrameTypeError(DomainError):
    """Raised when a frame family is explicit but unsupported."""

    def __init__(self, frame_type: str):
        super().__init__(f"Frame type '{frame_type}' is not supported by the current runtime.")


class LanguageNotFoundError(DomainError):
    """Raised when the deployed runtime does not expose a requested language."""

    def __init__(self, lang_code: str):
        super().__init__(f"Language '{lang_code}' is not supported by the deployed runtime.")


class LexiconEntryNotFoundError(DomainError):
    """Raised when a required lexical entry cannot be resolved."""

    def __init__(self, identifier: str, lang_code: str):
        super().__init__(f"Lexicon entry '{identifier}' not found for language '{lang_code}'.")


class PlanningError(DomainError):
    """Raised when canonical planning fails."""


class LexicalResolutionError(DomainError):
    """Raised when a ConstructionPlan cannot be lexicalized."""


class RealizationError(DomainError):
    """Raised when no configured renderer can realize a ConstructionPlan."""


class DeploymentError(DomainError):
    """Raised when required deployed runtime resources are unavailable."""
