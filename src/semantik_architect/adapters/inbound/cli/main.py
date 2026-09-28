from __future__ import annotations
import argparse, json, sys
from pathlib import Path
from ..python_sdk import SemantikArchitect
from ....domain.errors import SemantikArchitectError


def _load(path:str)->dict:
    if path=='-': return json.load(sys.stdin)
    return json.loads(Path(path).read_text(encoding='utf-8'))

def main(argv:list[str]|None=None)->int:
    p=argparse.ArgumentParser(prog='semantik-architect')
    p.add_argument('--runtime-root',default='runtime')
    sub=p.add_subparsers(dest='command',required=True)
    for name in ('render','validate-request','explain'):
        sp=sub.add_parser(name); sp.add_argument('request',help='request JSON path or - for stdin')
    sub.add_parser('capabilities')
    vr=sub.add_parser('validate-runtime'); vr.add_argument('runtime_set_id')
    cf=sub.add_parser('conformance'); cf.add_argument('suite', nargs='?'); cf.add_argument('--suite', dest='suite_option'); cf.add_argument('--runtime-set-id'); cf.add_argument('--output'); cf.add_argument('--candidate-dir')
    sv=sub.add_parser('serve'); sv.add_argument('--host',default='127.0.0.1'); sv.add_argument('--port',type=int,default=8765)
    args=p.parse_args(argv); app=SemantikArchitect.from_runtime_root(args.runtime_root)
    try:
        if args.command=='render': out=app.render(_load(args.request))
        elif args.command=='validate-request': out=app.validate_request(_load(args.request))
        elif args.command=='explain': out=app.explain(_load(args.request))
        elif args.command=='capabilities': out=app.capabilities()
        elif args.command=='validate-runtime': out=app.validate_runtime(args.runtime_set_id)
        elif args.command=='conformance':
            from ....conformance.harness import ConformanceHarness
            suite_path=args.suite_option or args.suite
            if not suite_path or (args.suite and args.suite_option): raise ValueError('Provide exactly one suite path')
            suite=_load(suite_path)
            if args.runtime_set_id and suite['runtime_set_id'] != args.runtime_set_id: raise ValueError('Suite runtime identity mismatch')
            if args.candidate_dir:
                from ....conformance.candidate import CandidateConformance
                candidate=CandidateConformance(args.candidate_dir,args.runtime_set_id or suite['runtime_set_id'])
                if Path(suite_path).resolve() != candidate.root/'conformance.suite.json': raise ValueError('Suite must be the locked candidate suite')
                app=candidate
            out=ConformanceHarness(app).run(suite).to_dict()
            if args.output:
                target=Path(args.output); target.parent.mkdir(parents=True,exist_ok=True)
                target.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        else:
            from ..http import serve
            serve(args.runtime_root,args.host,args.port); return 0
        print(json.dumps(out,ensure_ascii=False,indent=2)); return 1 if (args.command=='conformance' and not out.get('passed')) or (args.command=='validate-runtime' and not out.get('valid')) else 0
    except SemantikArchitectError as exc:
        print(json.dumps(exc.to_dict(),ensure_ascii=False,indent=2),file=sys.stderr); return 2
    except (KeyError,TypeError,ValueError,json.JSONDecodeError) as exc:
        err={"schema_version":"1.0","code":"SA-REQ-001","category":"REQUEST_INVALID","stage":"validation","message_safe":str(exc),"retryable":False}
        print(json.dumps(err,ensure_ascii=False,indent=2),file=sys.stderr); return 2

if __name__=='__main__': raise SystemExit(main())
