# Use pure data-driven table and immutable dataclasses for EU AI Act obligations

Status: accepted (generated, pending human review)

## Context

The EU AI Act dates and requirements are subject to regulatory amendments (e.g. Regulation (EU) 2026/1744). The library needs to be adaptable while maintaining determinism, strict immutability, zero runtime dependencies, and full testability without network or system clocks.

## Decision

Represent obligations and rules as frozen dataclasses (`ObligationRow`, `Obligation`, `Answers`, `Assessment`) with an overridable `DEFAULT_TABLE` mapping. The assessment logic executes pure functions comparing answers against regulatory conditions and deriving application dates.

## Consequences

Users can supply customized tables when amendments shift application dates; the library remains pure, fast, fully typed, and easily tested against literal acceptance specifications.
