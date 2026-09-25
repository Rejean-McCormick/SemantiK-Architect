from __future__ import annotations
from pathlib import Path
from dataclasses import dataclass

from ..adapters.runtime.filesystem import FilesystemRuntimeCatalog, ManifestCapabilityAdapter
from ..adapters.lexical.local_lexicon import RuntimeJsonLexiconAdapter
from ..adapters.realization.gf import GfBridgeRealizer
from ..adapters.locale import BasicLocaleDataAdapter
from ..observability import NullTelemetry
from ..application.use_cases import RenderCommunication, ValidateRequest, ListCapabilities, ValidateRuntime, ExplainGeneration
from ..conformance import RuntimeReleaseValidator

@dataclass(slots=True)
class ApplicationContainer:
    render: RenderCommunication
    validate_request: ValidateRequest
    list_capabilities: ListCapabilities
    validate_runtime: ValidateRuntime
    explain: ExplainGeneration


def build_container(runtime_root:str|Path, *, sa_version:str="1.0.0", realizer=None)->ApplicationContainer:
    catalog=FilesystemRuntimeCatalog(runtime_root,sa_version=sa_version)
    capabilities=ManifestCapabilityAdapter()
    locale_data=BasicLocaleDataAdapter()
    lexicon=RuntimeJsonLexiconAdapter(locale_data=locale_data)
    realizer=realizer or GfBridgeRealizer()
    return ApplicationContainer(
        render=RenderCommunication(runtime_catalog=catalog,capabilities=capabilities,lexical_knowledge=lexicon,lexical_binding=lexicon,realizer=realizer,sa_version=sa_version,telemetry=NullTelemetry()),
        validate_request=ValidateRequest(),
        list_capabilities=ListCapabilities(catalog),
        validate_runtime=ValidateRuntime(RuntimeReleaseValidator(catalog,capabilities)),
        explain=ExplainGeneration(catalog,lexicon),
    )
