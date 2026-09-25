from __future__ import annotations
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from ..python_sdk import SemantikArchitect
from ....domain.errors import SemantikArchitectError

class _Handler(BaseHTTPRequestHandler):
    app:SemantikArchitect
    server_version='SemantikArchitectHTTP/1.0'
    def _send(self,status:int,payload:Any)->None:
        body=json.dumps(payload,ensure_ascii=False).encode('utf-8'); self.send_response(status); self.send_header('Content-Type','application/json; charset=utf-8'); self.send_header('Content-Length',str(len(body))); self.end_headers(); self.wfile.write(body)
    def _body(self)->dict:
        length=int(self.headers.get('Content-Length','0')); raw=self.rfile.read(length); data=json.loads(raw.decode('utf-8')); assert isinstance(data,dict); return data
    def do_GET(self):
        try:
            if self.path=='/health': self._send(200,{"status":"ok"}); return
            if self.path=='/ready':
                caps=self.app.capabilities(); reports=[self.app.validate_runtime(runtime_id) for runtime_id in caps]
                ready=any(report.get("valid") for report in reports)
                self._send(200 if ready else 503,{"status":"ready" if ready else "not_ready","runtime_sets":reports}); return
            if self.path=='/v1/capabilities': self._send(200,self.app.capabilities()); return
            self._send(404,{"error":"not_found"})
        except Exception as exc: self._error(exc)
    def do_POST(self):
        try:
            data=self._body()
            if self.path=='/v1/render': self._send(200,self.app.render(data)); return
            if self.path=='/v1/validate-request': self._send(200,self.app.validate_request(data)); return
            if self.path=='/v1/explain': self._send(200,self.app.explain(data)); return
            self._send(404,{"error":"not_found"})
        except Exception as exc: self._error(exc)
    def _error(self,exc:Exception)->None:
        if isinstance(exc,SemantikArchitectError): self._send(422,exc.to_dict()); return
        self._send(400,{"schema_version":"1.0","code":"SA-REQ-001","category":"REQUEST_INVALID","stage":"validation","message_safe":str(exc),"retryable":False})
    def log_message(self,format,*args): return

def serve(runtime_root:str|Path='runtime',host:str='127.0.0.1',port:int=8765)->None:
    handler=type('SemantikHandler',(_Handler,),{'app':SemantikArchitect.from_runtime_root(runtime_root)})
    server=ThreadingHTTPServer((host,port),handler)
    try: server.serve_forever()
    finally: server.server_close()
