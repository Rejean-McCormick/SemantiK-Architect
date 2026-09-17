"""Infrastructure adapters for the SemantiK Architect runtime.

The runtime keeps only adapters needed to consume semantic input and precompiled
PGF assets: HTTP API, local runtime persistence, external knowledge lookups,
and GF/PGF realization. Grammar-development queues and message brokers live
outside this product boundary.
"""
