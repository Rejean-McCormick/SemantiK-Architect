# Defluens core candidate v0.8 — SemantiK public inbound profile

The development-only profile `profiles/defluens-core-1/` adds no second semantic/planning engine. It adapts bounded user selections (one to eight semantic statements) into the **existing** canonical `CommunicationRequest` schema. The existing `CommunicationPlanner`, `GenericLanguagePlanner`, `RuntimeJsonLexiconAdapter`, `GfBridgeRealizer`, `CandidateConformance`, and coverage validator remain authoritative.

Operations: `clause.copular_attribute`, `clause.copular_classification`, `clause.intransitive_event`, `clause.transitive_event`, `clause.locative`, `directive.action`. Two candidate runtimes: `defluens-core-fr-1`, `defluens-core-en-1`, each with its own locked PGF, bridge, lexicon, profile and suite. They are not part of the production runtime catalog, and no production activation is performed.

Public CLI:

```bash
PYTHONPATH=src python -m semantik_architect.adapters.inbound.cli.main defluens-core-catalog
PYTHONPATH=src python -m semantik_architect.adapters.inbound.cli.main defluens-core-request - < recipe.json
```

Example recipe:

```json
{
  "language": "fr",
  "items": [
    {"intent":"attribute","subject":"mira","concept":"ready","polarity":"negative","tense":"present"},
    {"intent":"transitive","subject":"lea","concept":"carry","object":"book","polarity":"positive","tense":"past"},
    {"intent":"directive","concept":"wait","polarity":"negative"}
  ]
}
```

The `CommunicationRequest` emitted by the CLI includes explicit semantic roles, required obligations, polarity and tense qualifiers, and the immutable candidate selector; there is no English-pivot translation, no free-text interpretation and no surface sentence template. All GF expressions are composed from fixed lexical entries and versioned bridge placeholders, never from browser-supplied GF syntax.

Status is CANDIDATE, not RELEASED. A missing GF 3.12 compile or missing lexical ability fails closed. Real PGF execution and native linguistic review remain unverified in this delivery.
