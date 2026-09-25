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
    cf=sub.add_parser('conformance'); cf.add_argument('suite')
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
            out=ConformanceHarness(app).run_file(args.suite).to_dict()
        else:
            from ..http import serve
            serve(args.runtime_root,args.host,args.port); return 0
        print(json.dumps(out,ensure_ascii=False,indent=2)); return 0
    except SemantikArchitectError as exc:
        print(json.dumps(exc.to_dict(),ensure_ascii=False,indent=2),file=sys.stderr); return 2
    except (KeyError,TypeError,ValueError,json.JSONDecodeError) as exc:
        err={"schema_version":"1.0","code":"SA-REQ-001","category":"REQUEST_INVALID","stage":"validation","message_safe":str(exc),"retryable":False}
        print(json.dumps(err,ensure_ascii=False,indent=2),file=sys.stderr); return 2

if __name__=='__main__': raise SystemExit(main())
