"""Exercise SemantiK's existing CandidateConformance against a private UNESCO candidate.

Never creates a RuntimeSet, authorizes publication or generates substitute text.
Run after GF Wordbench has compiled and locked grammar.pgf.
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import re
import sys

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT/'src') not in sys.path:
    sys.path.insert(0,str(ROOT/'src'))

SAFE = re.compile(r'^[a-zA-Z0-9._-]+\.json$')

def run(candidate: Path, requests_dir: Path, results_dir: Path, gf_exe: Path | None) -> dict:
    candidate=candidate.resolve(strict=True)
    requests_dir=requests_dir.resolve(strict=True)
    if any(p.is_symlink() or not p.is_dir() for p in (candidate,requests_dir)):
        raise ValueError('répertoires non fiables')
    results_dir=results_dir.resolve()
    if results_dir.exists() and any(results_dir.iterdir()):
        raise ValueError('répertoire des résultats non vide; aucune substitution de résultats existants')
    results_dir.mkdir(parents=True,exist_ok=True)
    if gf_exe is not None:
        gf_exe=gf_exe.resolve(strict=True)
        if gf_exe.name.lower() not in {'gf.exe','gf'} or not gf_exe.is_file():
            raise ValueError('exécutable gf.exe invalide')
        os.environ['SEMANTIK_GF_EXECUTABLE']=str(gf_exe)
    from semantik_architect.conformance.candidate import CandidateConformance
    from semantik_architect.conformance.harness import ConformanceHarness
    from semantik_architect.domain.communication.request import CommunicationRequest
    from semantik_architect.application.validation.request_validation import RequestValidator

    lock=json.loads((candidate/'pipeline.lock.json').read_text(encoding='utf-8'))
    app=CandidateConformance(candidate,lock['runtime_set_id'])
    suite=json.loads((candidate/'conformance.suite.json').read_text(encoding='utf-8'))
    report=ConformanceHarness(app).run(suite).to_dict()
    (candidate/'conformance.report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    if not report.get('passed'):
        return {'status':'BLOCKED_CONFORMANCE','report':report,'publication_authorized':False}
    count=0
    for filename in sorted(requests_dir.iterdir()):
        if filename.is_symlink() or not filename.is_file() or not SAFE.fullmatch(filename.name):
            raise ValueError('fichier de requête non sûr')
        if filename.stat().st_size>2_000_000: raise ValueError('requête trop volumineuse')
        data=json.loads(filename.read_text(encoding='utf-8'))
        RequestValidator().validate(CommunicationRequest.from_dict(data))
        actual=app.render(data)
        target=results_dir/filename.name
        target.write_text(json.dumps(actual,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        count+=1
    if count == 0: raise ValueError('aucune requête à réaliser')
    return {'status':'PASS_REAL_CANDIDATE_PGF_NOT_RELEASED','result_count':count,
            'runtime_set_id': lock['runtime_set_id'],'publication_authorized':False}

def main(argv=None) -> int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--candidate',type=Path,required=True)
    p.add_argument('--requests-dir',type=Path,required=True)
    p.add_argument('--results-dir',type=Path,required=True)
    p.add_argument('--gf-exe',type=Path)
    a=p.parse_args(argv)
    try:
        result=run(a.candidate,a.requests_dir,a.results_dir,a.gf_exe)
        code=0 if result['status']=='PASS_REAL_CANDIDATE_PGF_NOT_RELEASED' else 2
    except (OSError,ValueError,KeyError,RuntimeError,LookupError) as exc:
        result={'status':'BLOCKED','error':f'{type(exc).__name__}: {exc}',
                'publication_authorized':False}
        code=2
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return code

if __name__=='__main__': raise SystemExit(main())
