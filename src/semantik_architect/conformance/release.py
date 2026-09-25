from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..adapters.runtime.filesystem.capabilities import ManifestCapabilityAdapter
from ..application.ports.runtime_catalog import RuntimeCatalogPort
from ..domain.language.operations import V1_OPERATION_IDS


class RuntimeReleaseValidator:
    """Cross-validates a RuntimeSet beyond simple artifact hashing."""

    def __init__(
        self,
        catalog: RuntimeCatalogPort,
        capabilities: ManifestCapabilityAdapter,
    ) -> None:
        self.catalog = catalog
        self.capabilities = capabilities

    @staticmethod
    def _load_json(path: Path) -> dict[str, Any]:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError(f"Expected JSON object: {path}")
        return data

    def validate(self, runtime_set_id: str) -> dict[str, Any]:
        base = self.catalog.validate(runtime_set_id)
        errors = list(base.get("errors", []))
        descriptor = next(
            (item for item in self.catalog.list_runtime_sets() if item.runtime_set_id == runtime_set_id),
            None,
        )
        if descriptor is None:
            return {"runtime_set_id": runtime_set_id, "valid": False, "errors": errors or ["runtime_set_not_found"]}

        grammar = descriptor.artifacts_of_type("grammar")
        if len(grammar) != 1:
            errors.append(f"grammar_artifact_count:{len(grammar)}")

        bridge_artifacts = [
            artifact
            for artifact in descriptor.artifacts
            if artifact.artifact_type == "other"
            and artifact.artifact_id.startswith("sa-gf-bridge")
        ]
        bridge_operations: set[str] = set()
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

        evidence_refs = set(descriptor.manifest.get("conformance_evidence_refs", []))
        languages = descriptor.capability_manifest.get("languages", {})
        if not isinstance(languages, dict):
            errors.append("invalid_capability_languages")
            languages = {}

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
                missing_ops = sorted(set(profile.required_operations) - bridge_operations)
                if missing_ops:
                    errors.append(
                        f"profile_bridge_operations_missing:{language}:{identity}:{','.join(missing_ops)}"
                    )

        return {
            "runtime_set_id": runtime_set_id,
            "valid": not errors,
            "errors": errors,
        }
