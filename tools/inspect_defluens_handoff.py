"""Check the WordBench practical handoff against existing SA operation IDs.

Read-only discovery / contract-gap analysis, NOT SA conformance or release.
No new semantic planner, bridge grammar, or lexical policy is implemented here.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys

from semantik_architect.domain.language.operations import V1_OPERATION_IDS

EXPECTED = frozenset(('factual-present','past-event','past-state','future-reference','factual-negation',
    'temporal-order','condition-real','possibility','source-attribution','quantity','location',
    'instruction','prohibition','obligation','conditional-instruction'))


def inspect_handoff(data: dict) -> dict:
    if not isinstance(data,dict) or data.get('schema_id')!='defluens.wordbench-sa-development-handoff' or data.get('schema_version')!='1.0':
        raise ValueError('Unsupported development handoff schema')
    if any(data.get(k) is not False for k in ('sa_conformance_passed','release_ready','publication_authorized')):
        raise ValueError('Development evidence must never claim conformance or publication')
    rows=data.get('rows')
    if not isinstance(rows,list) or not rows: raise ValueError('Missing development evidence rows')
    issues=[]; grouped={}; keys=set()
    for row in rows:
        if not isinstance(row,dict):raise ValueError('Invalid handoff row')
        lang=row.get('language'); scenario=row.get('scenario_id'); op=row.get('sa_operation_candidate')
        key=(lang,scenario)
        if not isinstance(lang,str) or scenario not in EXPECTED or key in keys:
            raise ValueError('Duplicated or invalid language/scenario')
        keys.add(key)
        if op is not None and op not in V1_OPERATION_IDS:
            issues.append({'language':lang,'scenario_id':scenario,'issue':'unknown_sa_operation','operation':op})
        if op is None:
            issues.append({'language':lang,'scenario_id':scenario,'issue':'sa_bridge_contract_gap'})
        elif row.get('mapping_status')!='operation_candidate':
            issues.append({'language':lang,'scenario_id':scenario,'issue':'feature_or_contract_conformance_missing'})
        if row.get('gf_status')!='candidate_for_review':
            issues.append({'language':lang,'scenario_id':scenario,'issue':'gf_probe_not_candidate'})
        grouped.setdefault(lang,set()).add(scenario)
    for lang,scenarios in grouped.items():
        if scenarios != EXPECTED:issues.append({'language':lang,'issue':'incomplete_15_capabilities'})
    return {'schema_id':'semantik.defluens-handoff-inspection','schema_version':'1.0',
            'status':'DEVELOPMENT_ONLY', 'sa_candidate_bundle_ready':False,
            'sa_conformance_verified':False,'runtime_released':False,'publication_authorized':False,
            'language_count':len(grouped),'scenario_count':len(rows),
            'contract_gap_count':sum(x['issue']=='sa_bridge_contract_gap' for x in issues),
            'issues':issues,
            'next_steps':['Build immutable PGF and lexical artifacts in GF WordBench',
                          'Create versioned SA-GF bridge implementations for missing semantics',
                          'Run existing SemantiK candidate conformance before release']}


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('handoff',type=Path)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args(argv)
    try:
        result=inspect_handoff(json.loads(args.handoff.read_text(encoding='utf-8')))
        output=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
        if args.output:
            args.output.parent.mkdir(parents=True,exist_ok=True)
            args.output.write_text(output,encoding='utf-8')
        print(output)
        return 0
    except (OSError,ValueError,TypeError,KeyError) as exc:
        print(f'Invalid handoff: {exc}',file=sys.stderr);return 2

if __name__=='__main__':raise SystemExit(main())
