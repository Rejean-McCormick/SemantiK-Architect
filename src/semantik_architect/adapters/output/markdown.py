from __future__ import annotations
from ...domain.communication.result import CommunicationResult

def project_markdown(result:CommunicationResult)->str:
    lines=[]
    for b in result.blocks:
        if b.kind=='list': lines.extend(f"- {i.text}" for i in b.items)
        elif b.kind=='heading': lines.append(f"## {b.text or ''}")
        elif b.kind=='label_value': lines.append(f"**{b.label or ''}:** {b.value or ''}")
        elif b.text: lines.append(b.text)
    return "\n\n".join(lines)
