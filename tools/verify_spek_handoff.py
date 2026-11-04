"""Independent SemantiK Architect contract preflight for a private Spek handoff.

This checks the existing CommunicationRequest/1.0, not GF realization.
It does not select semantic facts, check rhetorical entailment or authorize publication.
Run as: python tools/verify_spek_handoff.py --lock ... --requests-dir ...
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re

from semantik_architect.domain.communication.request import CommunicationRequest
from semantik_architect.application.validation.request_validation import RequestValidator

HANDOFF='spek.private-editorial-handoff/1.0'
SAFE_FILENAME=re.compile(r'^[a-zA-Z0-9._-]+\.json$')

class HandoffError(ValueError): pass


def verify(lock: dict, requests_dir: Path) -> dict:
    if (not isinstance(lock,dict) or lock.get('format')!=HANDOFF or
        lock.get('status')!='PRIVATE_UNQUALIFIED_NOT_PUBLISHABLE'):
        raise HandoffError('Unapproved private Spek handoff required')
    fields=lock.get('fields')
    if not isinstance(fields,list) or not fields:
        raise HandoffError('No explicit linguistic fields')
    root=Path(requests_dir)
    if root.is_symlink() or not root.is_dir():
        raise HandoffError('Private request directory missing or unsafe')
    request_ids=set(); request_files=set(); validator=RequestValidator()
    for field in fields:
        if not isinstance(field,dict):
            raise HandoffError('Malformed language field')
        filename=field.get('request_file')
        if not isinstance(filename,str) or not SAFE_FILENAME.fullmatch(filename):
            raise HandoffError('Unsafe request filename')
        if filename in request_files:
            raise HandoffError('Duplicate request filename in editorial handoff')
        request_files.add(filename)
        path=root/filename
        if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(root.resolve()) or path.stat().st_size>2_000_000:
            raise HandoffError('Request missing or unsafe')
        digest='sha256:'+hashlib.sha256(path.read_bytes()).hexdigest()
        if digest!=field.get('request_sha256'):
            raise HandoffError('Request digest changed')
        try:
            raw=json.loads(path.read_text(encoding='utf-8'))
            request=CommunicationRequest.from_dict(raw)
            validator.validate(request)
        except (ValueError,KeyError,TypeError) as exc:
            raise HandoffError('SemantiK request contract invalid') from exc
        # No planning hints are introduced here: semantic graph and obligations
        # stay entirely owned by the upstream author/editor.
        if request.context.target_language!=lock.get('language'):
            raise HandoffError('Language mismatch')
        force=field.get('required_force')
        if force not in {'ASSERT','PRESENT','ASK'} or any(o.force.value!=force for o in request.obligations):
            raise HandoffError('Obligation force incompatible with Spek slot')
        source_refs={ref for o in request.obligations for ref in o.source_refs}
        if source_refs!=set(field.get('source_assertion_refs',[])):
            raise HandoffError('Required sources do not match editorial selection')
        allowed=set(field.get('allowed_block_kinds',[]))
        if not allowed or not set(request.constraints.allowed_block_kinds).intersection(allowed):
            raise HandoffError('No compatible SemantiK output block')
        if request.request_id and request.request_id in request_ids:
            raise HandoffError('Duplicate request IDs in editorial handoff')
        if request.request_id:request_ids.add(request.request_id)
    return {'format':'semantik.spek-handoff-preflight/1.0',
            'status':'PASS_REQUEST_CONTRACT_ONLY','request_count':len(fields),
            'gf_pgf_execution_verified':False,'rhetorical_relations_verified':False,
            'publication_authorized':False}


def main(argv=None):
    p=argparse.ArgumentParser(description='Preflight private Spek requests against SemantiK v1 contract')
    p.add_argument('--lock',required=True,type=Path)
    p.add_argument('--requests-dir',required=True,type=Path)
    a=p.parse_args(argv)
    try:
        result=verify(json.loads(a.lock.read_text(encoding='utf-8')),a.requests_dir)
    except (ValueError,OSError,KeyError) as exc:
        p.exit(2,'REFUSED: '+str(exc)+'\n')
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0


if __name__=='__main__':raise SystemExit(main())
