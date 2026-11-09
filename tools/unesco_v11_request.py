"""Produce one bounded communication request from a reviewed v11 UNESCO handoff.

Requires local source file, writes a NEW private JSON request. It never
instantiates a runtime, compiles GF, approves assertions or publishes.
"""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from semantik_architect.adapters.ecosystem.unesco_v11 import build_request,UNESCOProjectionError

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--handoff',required=True,type=Path)
    p.add_argument('--unesco-id',required=True)
    p.add_argument('--profile',default='defluens-core-1')
    p.add_argument('--out',required=True,type=Path)
    a=p.parse_args(argv)
    try:
        if not a.handoff.is_file() or a.handoff.stat().st_size>8_000_000:
            raise UNESCOProjectionError('Input must be an existing bounded v11 handoff')
        obj=json.loads(a.handoff.read_text('utf8'))
        request=build_request(obj,unesco_id=a.unesco_id,capability_profile=a.profile)
        out=a.out.resolve()
        if out.exists() or any((p/'.git').exists() for p in out.parents):
            raise UNESCOProjectionError('New private output outside Git required')
        out.parent.mkdir(parents=True,exist_ok=True)
        with out.open('x',encoding='utf8') as f:json.dump(request.to_dict(),f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n')
        print(json.dumps({'status':'REQUEST_STRUCTURALLY_VALID_RUNTIME_UNQUALIFIED',
                          'request_id':request.request_id,'publication':'BLOCKED','out':str(out)}));return 0
    except (UNESCOProjectionError,ValueError,KeyError,TypeError,OSError) as e:
        print(json.dumps({'status':'BLOCKED','error':str(e)}),file=sys.stderr);return 2
if __name__=='__main__':raise SystemExit(main())
