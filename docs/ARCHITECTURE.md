# Architecture and contracts

The instruction skill and local tooling are separate. Installing the skill does not install Python, invoke an API, or execute files.

| Layer | Location | Responsibility |
|---|---|---|
| Assistant behavior | `skills/copywriter-master/SKILL.md` | Modes, routing, requested scope, editorial review |
| Knowledge | `skills/copywriter-master/references/` | Strategy, examples, sector review prompts and source limits |
| Contracts | `skills/copywriter-master/schemas/` and `runtime-contract.json` | Strict brief/output, batch and event contracts |
| Rule catalog | `skills/copywriter-master/rules/validation.json` | Stable finding codes, risk priority, category, remediation, pattern signals |
| Execution | `copywriter_runtime/` | Deterministic validation, batch workflow, report rendering, explicit event logging |
| Entrypoints | `tools/copywriter.py`, `tools/validate_copy.py` | Friendly CLI and compatible version 1.2 wrapper |
| Evaluation | `tools/evaluate.py`, `evaluation/` | Fixed human-reviewed model protocol and separate synthetic deterministic regressions |
| Release | `tools/release.py` | Lint, deterministic ZIP, file manifest, checksums and verification |

The public local API is `from copywriter_runtime import validate_copy, InputError`. Pass two parsed JSON objects matching the schemas. It returns a serializable report and does not store data. Invalid structured input raises `InputError`. An integration owns file access, network services, authentication and publishing; no HTTP server or model-generation service is included.

The engine executes a fixed implementation. The rule catalog configures finding metadata and known signal patterns, not arbitrary Python or instructions from a brief. The brief is trusted configuration maintained by its owner; the draft cannot override it. Rules sort by critical/high/medium/low priority. A pattern is a review signal, not a legal decision. Every valid report retains human review, including when no pattern fires.

Contract versions are independent of release versions. Release 1.3.1 retains skill/runtime/brief/output/report contract `1.0` and editorial rubric `1.1.0`. Report fields added in 1.3 are additive: rule-catalog version/hash, categories, priorities and remediation. Consumers must tolerate additive report fields. Brief/output schemas remain strict; a new input field needs a versioned migration.

The schema IDs are identifiers; validation does not fetch them or sources. No module performs network calls. Logging is off unless the caller supplies `--log`. Raw model outputs, personal identifiers, and private brief/source text are excluded from event fields. Optional event fingerprints provide correlation, not proof of authenticity. Release checksums detect accidental alteration, not a trusted publisher signature.
