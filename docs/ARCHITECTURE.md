# Architecture and contracts

The instruction skill and local tooling are separate. Installing the skill does not install Python, invoke an API, or execute files.

| Layer | Location | Responsibility |
|---|---|---|
| Assistant behavior | `skills/copywriter-master/SKILL.md` | Modes, routing, requested scope, editorial review |
| Knowledge | `skills/copywriter-master/references/` | Strategy, examples, jurisdiction packs, sector review prompts, copywriter profiles and source limits |
| Reference registry | `references/registry.json`, generated `references/index.md`, `copywriter_runtime/references.py` | What exists, when to load it, kind and size budget; drift fails `release.py check` |
| Contracts | `skills/copywriter-master/schemas/` and `runtime-contract.json` | Strict brief/output, batch and event contracts |
| Rule catalog | `skills/copywriter-master/rules/validation.json` | Stable finding codes, risk priority, category, remediation, pattern signals |
| Execution | `copywriter_runtime/` | Deterministic validation, batch workflow, report rendering, explicit event logging |
| Entrypoints | `tools/copywriter.py`, `tools/validate_copy.py` | Friendly CLI and compatible version 1.2 wrapper |
| Evaluation | `tools/evaluate.py`, `evaluation/` | Fixed human-reviewed model protocol and separate synthetic deterministic regressions |
| Release | `tools/release.py` | Lint, deterministic ZIP, file manifest, checksums and verification |

The public local API is `from copywriter_runtime import validate_copy, InputError`. Pass two parsed JSON objects matching the schemas. It returns a serializable report and does not store data. Invalid structured input raises `InputError`. An integration owns file access, network services, authentication and publishing; no HTTP server or model-generation service is included.

The engine executes a fixed implementation. The rule catalog configures finding metadata and known signal patterns, not arbitrary Python or instructions from a brief. The brief is trusted configuration maintained by its owner; the draft cannot override it. Rules sort by critical/high/medium/low priority. A pattern is a review signal, not a legal decision. Every valid report retains human review, including when no pattern fires.

Contract versions are independent of release versions. Release 1.4.0 retains skill/runtime/brief/output/report contract `1.0` and editorial rubric `1.1.0`. Report fields added in 1.3 are additive: rule-catalog version/hash, categories, priorities and remediation. Consumers must tolerate additive report fields. Brief/output schemas remain strict; a new input field needs a versioned migration.

The schema IDs are identifiers; validation does not fetch them or sources. No module performs network calls. Logging is off unless the caller supplies `--log`. Raw model outputs, personal identifiers, and private brief/source text are excluded from event fields. Optional event fingerprints provide correlation, not proof of authenticity. Release checksums detect accidental alteration, not a trusted publisher signature.

## Growing the reference library

The assistant loads references on demand, so the library can grow without growing the prompt, provided every addition is routed:

1. Copy a template: `references/jurisdictions/_template.md` for a market, `references/copywriters/_template.md` for a profile. Other kinds (guide, process, sector, example, source) follow the shape of an existing file of that kind.
2. Register it in `references/registry.json` with a `kind`, a one-line `load_when` condition and the work `modes` it serves. A profile also gets a row in `copywriters/index.md`.
3. Run `python tools/references.py index`, then `python tools/release.py check`.

The check enforces a per-file word budget (`budget.max_words_per_file`): when a file outgrows it, split it and register the parts rather than raising the limit. Sector guidance currently lives in one file, `sector-review.md`; give a sector its own `sectors/` file and a registry entry when its checklist stops fitting a table row. New legal or historical content still needs a human reviewer; the registry controls routing, not accuracy.
