# Canonical Examples

Status: **informational examples constrained by locks**

## Orgo task bundle

Conceptually:

```text
SemanticGraph:
  Marcel (entity)
  machine 4356 (entity)
  repair (concept)
  16:00 (temporal value)
  Gabriel (entity)
  phone (literal)
  statement: repair event with patient machine 4356
  statement: deadline(repair, 16:00)
  statement: technical_contact(repair, Gabriel)
  statement: phone(Gabriel, ...)

Obligations:
  DIRECT repair/deadline to Marcel
  PRESENT technical contact and phone

Context:
  language=fr-CA
  register=operational
  relationship=familiar
```

Possible result:

```text
Marcel, la machine 4356 doit être réparée avant 16 h.
Gabriel est disponible pour t'aider au 418 123-4567.
```

No output wording is itself normative; obligation coverage and semantics are.

## eThikos confirmation

A concept map becomes semantic statements plus `ASK`/`PRESENT` obligations. SA renders a natural question/summary in the target language. The user confirms or edits the semantic structure; SA does not infer which argument is ethically correct.

## Multi-language segmentation

The same obligation set may yield two utterances in French and three in another released language if required for natural, faithful realization. The discharged obligation set must remain identical.
