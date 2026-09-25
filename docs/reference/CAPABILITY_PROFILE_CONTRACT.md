# Capability Profile Contract

Status: **normative reference**

A capability profile is a versioned workload promise. It defines what an application may rely on from a released language/runtime combination.

## Profile identity

Profile identity is `profile_id` + integer `profile_version`, displayed conventionally as `profile-id-N` (for example `orgo-operational-1`).

## Required content

A profile declares:

- required SA↔GF operation IDs;
- required language-planning/register features;
- required output block kinds;
- locale/format features;
- conformance test suite identity;
- optional parent profiles.

## Release meaning

`fr + orgo-operational-1 = RELEASED` means the exact active RuntimeSet has immutable passing evidence for every requirement in the profile. It does not mean “French probably works”.

## No partial profile

A profile is indivisible at production runtime. If one required operation is missing, that language/profile pair is not released.

## Profile evolution

- Additive new profile: no impact on existing profiles.
- New requirements to an existing profile: publish a new profile version.
- Never silently strengthen `profile-X-1` after release.
