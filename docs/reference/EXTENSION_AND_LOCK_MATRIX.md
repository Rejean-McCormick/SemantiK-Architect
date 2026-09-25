# Extension and Lock Matrix

Status: **normative reference**

| Concern | Locked? | Extension mechanism |
|---|---|---|
| canonical pipeline stages | yes | ADR + architecture lock update |
| `CommunicationRequest` top-level meaning | yes | schema major/minor rules |
| structural semantic node kinds | yes for v1 | schema/ADR change |
| semantic predicate vocabulary | no, intentionally extensible | namespace-qualified registry/ontology |
| semantic role vocabulary | no, intentionally extensible | namespace-qualified registry/ontology |
| communicative force baseline | yes | versioned registry change |
| output block kinds | yes for v1 | schema/version change |
| SA↔GF contract semantics | yes | semver + ADR for incompatible changes |
| SA↔GF operation catalog | extensible | additive minor versions; semantic changes major |
| capability profiles | extensible | new named/versioned profile |
| language count | extensible | artifacts + conformance evidence only |
| lexical sources | extensible | new adapter behind lexical ports |
| ecosystem integrations | extensible | new ACL adapter |
| output projections | extensible | new output adapter |
| stable error meanings/codes | yes | additive registry rules; no reuse |
| default architectural style | yes | ADR required |
| probabilistic runtime in canonical path | forbidden v1 | explicit ADR/major design change |
