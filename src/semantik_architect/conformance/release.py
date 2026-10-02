from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..adapters.runtime.filesystem.capabilities import ManifestCapabilityAdapter
from ..application.ports.runtime_catalog import RuntimeCatalogPort
from ..domain.language.operations import V1_OPERATION_IDS
from ..adapters.lexical.local_lexicon import RuntimeJsonLexiconAdapter

_MATH_OPERATIONS = frozenset({"math.informalize_formula"})


class RuntimeReleaseValidator:
    """Cross-validates a RuntimeSet beyond simple artifact hashing.

    Generic SA operations use the SA↔GF bridge. Mathematical articulation may
    instead use the ADR-0014 Informath backend. Backend requirements are derived
    from released capability profiles; candidate-only artifacts can therefore be
    integrity-valid without pretending to be release-ready.
    """

    def __init__(self, catalog: RuntimeCatalogPort, capabilities: ManifestCapabilityAdapter) -> None:
        self.catalog = catalog
        self.capabilities = capabilities

    @staticmethod
    def _load_json(path: Path) -> dict[str, Any]:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError(f"Expected JSON object: {path}")
        return data

    @staticmethod
    def _artifacts(descriptor, prefix: str):
        return [a for a in descriptor.artifacts if a.artifact_type == "other" and a.artifact_id.startswith(prefix)]

    def validate(self, runtime_set_id: str) -> dict[str, Any]:
        base = self.catalog.validate(runtime_set_id)
        errors = list(base.get("errors", []))
        descriptor = next((item for item in self.catalog.list_runtime_sets() if item.runtime_set_id == runtime_set_id), None)
        if descriptor is None:
            return {"runtime_set_id": runtime_set_id, "valid": False, "errors": errors or ["runtime_set_not_found"]}

        try:
            RuntimeJsonLexiconAdapter().validate_runtime(descriptor)
        except Exception as exc:
            errors.append(f"lexical_runtime_invalid:{exc}")

        languages = descriptor.capability_manifest.get("languages", {})
        if not isinstance(languages, dict):
            errors.append("invalid_capability_languages")
            languages = {}

        released_profiles: list[tuple[str, str, Any, str]] = []
        evidence_refs = set(descriptor.manifest.get("conformance_evidence_refs", []))
        for language, language_row in languages.items():
            if not isinstance(language_row, dict) or language_row.get("status") != "RELEASED":
                continue
            if not language_row.get("concrete"):
                errors.append(f"missing_concrete:{language}")
            for profile_row in language_row.get("profiles", []):
                if not isinstance(profile_row, dict) or profile_row.get("status") != "RELEASED":
                    continue
                identity = str(profile_row.get("profile_id") or "")
                evidence_ref = str(profile_row.get("evidence_ref") or "")
                if evidence_ref not in evidence_refs:
                    errors.append(f"profile_evidence_not_pinned:{language}:{identity}:{evidence_ref}")
                try:
                    profile = self.capabilities.get_profile(descriptor, identity)
                except Exception as exc:
                    errors.append(f"profile_invalid:{language}:{identity}:{exc}")
                    continue
                if profile is None:
                    errors.append(f"profile_artifact_missing:{language}:{identity}")
                    continue
                released_profiles.append((str(language), identity, profile, evidence_ref))

        generic_required = any(set(profile.required_operations) - _MATH_OPERATIONS for _, _, profile, _ in released_profiles)
        math_required = any(set(profile.required_operations) & _MATH_OPERATIONS for _, _, profile, _ in released_profiles)

        bridge_operations: set[str] = set()
        if generic_required:
            grammar = descriptor.artifacts_of_type("grammar")
            if len(grammar) != 1:
                errors.append(f"grammar_artifact_count:{len(grammar)}")
            bridge_artifacts = self._artifacts(descriptor, "sa-gf-bridge")
            if len(bridge_artifacts) != 1 or bridge_artifacts[0].path is None:
                errors.append(f"bridge_artifact_count:{len(bridge_artifacts)}")
            else:
                try:
                    bridge = self._load_json(bridge_artifacts[0].path)
                    if str(bridge.get("contract_version")) != descriptor.sa_gf_contract_version:
                        errors.append("bridge_contract_version_mismatch")
                    bridge_operations = set((bridge.get("operations") or {}).keys())
                    unknown = sorted(bridge_operations - V1_OPERATION_IDS)
                    if unknown:
                        errors.append(f"unknown_bridge_operations:{','.join(unknown)}")
                except Exception as exc:
                    errors.append(f"invalid_bridge_spec:{exc}")

        if math_required:
            configs = self._artifacts(descriptor, "informath-config")
            registries = self._artifacts(descriptor, "math-symbol-registry")
            if len(configs) != 1 or configs[0].path is None:
                errors.append(f"informath_config_artifact_count:{len(configs)}")
            else:
                try:
                    config = self._load_json(configs[0].path)
                    if config.get("schema_version") != "1.0" or not config.get("informath_version"):
                        errors.append("informath_config_invalid")
                except Exception as exc:
                    errors.append(f"informath_config_invalid:{exc}")
            if len(registries) != 1 or registries[0].path is None:
                errors.append(f"math_symbol_registry_artifact_count:{len(registries)}")
            else:
                try:
                    registry = self._load_json(registries[0].path)
                    if registry.get("schema_version") != "1.0" or not isinstance(registry.get("symbols"), dict):
                        errors.append("math_symbol_registry_invalid")
                except Exception as exc:
                    errors.append(f"math_symbol_registry_invalid:{exc}")

        for language, identity, profile, _ in released_profiles:
            required = set(profile.required_operations)
            generic_ops = required - _MATH_OPERATIONS
            math_ops = required & _MATH_OPERATIONS
            missing_generic = sorted(generic_ops - bridge_operations)
            if missing_generic:
                errors.append(f"profile_bridge_operations_missing:{language}:{identity}:{','.join(missing_generic)}")
            if math_ops and not math_required:
                errors.append(f"profile_math_backend_missing:{language}:{identity}")

        return {"runtime_set_id": runtime_set_id, "valid": not errors, "errors": errors}
