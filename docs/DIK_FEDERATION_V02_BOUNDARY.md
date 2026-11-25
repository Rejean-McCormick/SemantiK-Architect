# SemantiK Architect — typed semantic references from diK

**Candidate read-only coordination, 24 November 2026.** SemantiK Architect
accepts only typed, resolved semantics from the adopted owner contract;
it does not resolve an ambiguous word into an invented KQ or promote a
crosswalk candidate. Keep `namespace_id` with every local KQ/KP; a
Wikidata Q/P identifier is an external reviewed reference, not a substitute.

The existing V5.9 bridge remains non-authoritative. The diK V5.11
multirevision view remains blocked until a source has one fully inspected
revision or an explicit hash-pinned review for **derived lookup only**.
The new `/0.2` decision profile pins the inspected graph SHA-256 along with
the other four source digests; a `/0.1` selection must not be silently used
for a fresh build.

Realization/generation still requires separate lexical and GF bindings per
language, with explicit fallback status. Neither source lexical coverage
nor a selected view is a SemantiK RuntimeSet or publication approval.
