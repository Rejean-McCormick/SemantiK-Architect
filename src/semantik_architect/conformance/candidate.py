"""Offline conformance of an orchestrator staging bundle, never a serving runtime.

This path verifies pipeline.lock.json and exercises the real GF adapter. It
neither marks artifacts RELEASED nor writes activation or capability manifests.
"""
import hashlib
import json
from pathlib import Path
from ..application.ports.runtime_catalog import RuntimeArtifact, RuntimeSetDescriptor
from ..application.validation.request_validation import RequestValidator
from ..application.validation.coverage import CoverageValidator
from ..application.planning.communication_planner import CommunicationPlanner
from ..application.planning.language_planner import GenericLanguagePlanner
from ..application.output import OutputAssembler
from ..adapters.lexical.local_lexicon import RuntimeJsonLexiconAdapter
from ..adapters.locale import BasicLocaleDataAdapter
from ..adapters.realization.gf import GfBridgeRealizer
from ..adapters.runtime.filesystem.capabilities import ManifestCapabilityAdapter
from ..domain.communication.request import CommunicationRequest
from ..domain.errors import SemantikArchitectError


class CandidateConformance:
    def __init__(self, root, runtime_set_id, *, realizer=None):
        self.root = Path(root).resolve()
        self.lock = json.loads((self.root / 'pipeline.lock.json').read_text())
        if self.lock.get('runtime_set_id') != runtime_set_id:
            raise ValueError('Candidate identity does not match pipeline lock')
        required = {'grammar.pgf', 'bridge.json', 'lexicon.json', 'profile.json', 'conformance.suite.json'}
        if not required <= self.lock.get('inputs', {}).keys():
            raise ValueError('Incomplete pipeline lock')
        self.verify()
        kinds = [('grammar', 'grammar', 'grammar.pgf'), ('lexical', 'lexical', 'lexicon.json'),
                 ('other', 'sa-gf-bridge-v1', 'bridge.json'),
                 ('other', 'capability-profile-' + self.lock['profile_id'], 'profile.json')]
        self.runtime = RuntimeSetDescriptor(runtime_set_id, self.lock['sa_gf_contract_version'],
            'CANDIDATE', tuple(RuntimeArtifact(k, i, self.lock['inputs'][n], self.root/n) for k,i,n in kinds),
            {'languages': {self.lock['language']: {'status':'CANDIDATE', 'concrete':self.lock['concrete']}}}, {}, self.root)
        self.lexicon = RuntimeJsonLexiconAdapter(locale_data=BasicLocaleDataAdapter())
        self.realizer = realizer or GfBridgeRealizer()
        self.profile = ManifestCapabilityAdapter().get_profile(self.runtime, self.lock['profile_id'])
        if self.profile is None:
            raise ValueError('Candidate profile missing')

    def verify(self):
        for name, expected in self.lock['inputs'].items():
            file = (self.root/name).resolve()
            if not file.is_relative_to(self.root) or hashlib.sha256(file.read_bytes()).hexdigest() != expected:
                raise ValueError('Candidate artifact integrity failure: ' + name)

    def render(self, data):
        self.verify()
        request = CommunicationRequest.from_dict(data)
        RequestValidator().validate(request)
        if (request.context.target_language != self.lock['language'] or
            request.capability_profile != self.lock['profile_id'] or
            (request.runtime_selector and request.runtime_selector.runtime_set_id != self.runtime.runtime_set_id)):
            raise ValueError('Candidate request identity mismatch')
        cp = CommunicationPlanner().plan(request)
        lexical = self.lexicon.preflight(request, cp, self.runtime)
        plan = GenericLanguagePlanner().plan(request, cp, lexical)
        if ({u.operation_id for u in plan.units} - set(self.profile.required_operations) or
            {b.kind for b in plan.blocks} - set(self.profile.required_block_kinds)):
            raise ValueError('Candidate plan exceeds profile')
        coverage = CoverageValidator()
        coverage.validate_plan(request, plan)
        bindings = self.lexicon.bind(request, plan, lexical, self.runtime)
        realized = self.realizer.realize(plan, bindings, self.runtime)
        result = OutputAssembler().assemble(request, plan, realized, self.runtime, sa_version='1.0.0')
        coverage.validate_result(request, result.coverage)
        if request.constraints.max_length is not None and len(result.plain_text or '') > request.constraints.max_length:
            raise SemantikArchitectError('SA-CON-001', 'Candidate output exceeds max_length')
        return result.to_dict()
