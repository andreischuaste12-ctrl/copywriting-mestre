# Changelog

## 1.4.0 — 2026-11-02

- **Reference architecture.** `references/registry.json` is now the single source for what each reference is, when to load it, and its size budget. `references/index.md` is generated from it (`python tools/references.py index`), and `tools/release.py check` fails on an unregistered or missing reference, a stale index, a profile list that disagrees with the registry, a file over the word budget, a profile without a source note, or a jurisdiction pack without a not-legal-advice statement.
- Added `jurisdictions/` (Brazil guidance moved from `brazilian-compliance.md` to `jurisdictions/brazil.md`, content unchanged) plus jurisdiction and copywriter-profile templates, so new markets and profiles are additive. No new legal content was written; other markets remain starting-point links in `sector-review.md`.
- Four profiles (Bencivenga, Bernbach, Schwab, Schwartz) now carry an explicit source note stating that no primary link is listed.
- `SKILL.md` is shorter: the reference list points to the generated index, and the validation and feedback sections are condensed with no change in rules.
- **Installers.** Remote installs now download the release archive pinned to their own version and verify its SHA-256 against `SHA256SUMS` instead of fetching the `main` branch; `--sha256` / `-Sha256` accepts an out-of-band hash. The release workflow publishes the archive, `SHA256SUMS` and both installers as a GitHub Release. **A release must exist for remote install to work.** `release.py check` fails if an installer pin differs from `VERSION`.
- **Rule catalog 1.1.0.** New review-level `number_word_signal` flags quantities written as words (for example "dois mil", "two thousand"), which the numeric-token check cannot compare. `health_signal` no longer fires on the Portuguese idiom "se trata de" / "trata-se". Existing logs recorded with catalog 1.0.0 are rejected by `summary` because the catalog hash changed; keep them separate.
- `contains()` raises `InputError` on an empty phrase instead of `IndexError`. The event-log lock file now records the owner PID and time so a stale lock is recognizable.
- Maintainer tooling: `pyproject.toml` (ruff, mypy, coverage), `requirements-dev.txt`, a `quality` CI job with an 85% coverage gate, and `push` CI limited to `main` plus pull requests to avoid duplicate runs.
- The skill's behavior rules, schemas, report format and exit codes are unchanged. No live model benchmark was run; no performance claim is made.

## 1.3.1 — 2026-10-30

- Clarified that AIDA, PAS, BAB, draft angles and the framework library are illustrative rather than restrictive. Any suitable advertising/copywriting framework may be selected, adapted or combined; a named formula is optional.
- Preserved the existing runtime, schemas, rule catalog and editorial rubric.

## 1.3.0 — 2026-10-30

- Separated the offline runtime/API from CLI wrappers and reference knowledge; preserved the v1.2 validator entrypoint, strict brief/output schemas and exit codes.
- Added a versioned runtime contract, prioritized rule catalog, sector/market review worksheets and explicit compatibility evidence boundaries. Finding metadata is additive; existing report fields remain.
- Added an onboarding CLI, JSON/Markdown/HTML reporting, batch validation and explicit local JSONL events with concurrent-writer rejection and validated summaries. Logging stays off by default.
- Added six synthetic sector regressions and Portuguese/English quickstarts; no real campaign evidence or live model results are claimed.
- Added lint/build/verify tooling for reproducible installable archives, checksums, package manifests and a tag-triggered test/build artifact workflow.
- Added matched-run benchmark comparison reports that reject mixed contexts and label incomplete repetitions. The rubric remains independently versioned at 1.1.0.

## 1.2.0 — 2026-10-30

- Added installable JSON Schema Draft 2020-12 contracts for trusted briefs and structured final copy. Normal chat output remains proportional to the user request.
- Added an optional local Python validator for quantity, length, required/forbidden phrases, CTA wording, numeric tokens, exact registered claims, sources and authorization state. No AI API or automatic rewrite is used.
- Reports bind checks to brief/output fingerprints and distinguish detected violations from mandatory human review; passing checks do not certify truth, permission or conversion impact.
- Added Portuguese/English fixtures and adversarial regressions for changed prices/dates, omitted terms, invented numbers, missing sources, held claims, schema overrides, privacy signals and incomplete semantic coverage.
- Expanded CI definitions to Linux, macOS and Windows. These definitions do not establish that remote CI has run successfully.
- Kept the editorial rubric at 1.1.0 independently of the skill release, preserving the fixed evaluation suite. No live model benchmark or campaign performance results are claimed.

## 1.1.0 — 2026-10-30

- Added explicit Diagnose, Write, Review, Research, and CTA/offer modes, a decision tree, and a proportional output contract that preserves short copy-only requests.
- Added an anchored eight-dimension editorial rubric, a 13/16 readiness threshold, and independent hard failures for evidence, regulated promises, scarcity, terms, privacy, and scope.
- Added ten complete synthetic good/bad examples, fixed evaluation cases, manual scoring tools, and a matched baseline comparison protocol. No live model benchmark or conversion improvement is claimed.
- Added an opt-in feedback/case-record process; no telemetry or automatic persistent learning.
- Identified Andrei Schuaste as project author and copyright holder under the existing Apache-2.0 license; included LICENSE and NOTICE in the installable folder.
- Added repository, evaluation-tool, and installer checks for local validation and CI.

## 1.0.0 — baseline snapshot

The pre-versioning baseline is commit `3b22ed6`. The 1.0.0 label identifies that historical behavior for comparison; it was not previously tagged or released as 1.0.0. It includes proportional diagnosis, research synthesis, claim integrity, reference profiles, and installers. No historical benchmark scores are available.
