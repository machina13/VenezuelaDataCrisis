# Deduplication contract

This document defines the shared deduplication boundary for the staging
architecture.

## Architecture

Stage 1 ingests source data into staging. It may calculate deterministic
fingerprints and blocking keys, but it must not decide global merges across the
dataset.

Stage 2 owns global consolidation. It consumes staging records, applies entity
specific dedup specs, and generates `dedup_candidates` for review or downstream
serving.

Stage 3 serves consolidated data. It should consume the Stage 2 output rather
than reimplementing source-level dedup logic.

## Entity rules

`Event` records may auto-merge when their exact dedup fingerprint matches.

`AcopioCenter` records may auto-merge when their exact dedup fingerprint
matches.

`Person` records must never auto-merge. Person dedup only creates candidates
for human review because identity resolution is sensitive and may involve PII
derived tokens.

## Volatile fields

The following fields are volatile and must not participate in blocking,
fingerprints, or deterministic merge decisions:

- `status`
- `needs`
- `capacity`
- `confidence`
- `contacto`
- `description`
- `magnitude`
- `depth`
