# Changelog

## 1.4.0 — 2026-11-02

- **Unreleased 1.4.0 adjustments:** clarified that research-only requests do not produce copy. Markdown and HTML validation reports now include item IDs and finding messages; HTML uses a real table. Consumers parsing the old Markdown layout should update their parser; the JSON report structure and exit codes are unchanged. Semantic review now explicitly warns that an allowed number can be attached to an unsupported fact.
- **Rule catalog 1.2.0:** expanded the partial Portuguese/English number-word review signal to cover common teens, tens and hundreds. This is not a complete parser or a fact check; ambiguous articles remain excluded. The catalog hash changed: summarize old event logs using their matching runtime/catalog and keep them separate from new logs.
- Pinned CI actions to commit hashes using Node 24 releases; ignored local coverage files. No live model benchmark, independent legal review, or complete primary-source verification is claimed.

- **Reference architecture.** `references/registry.json` is now the single source for what each reference is, when to load it, and its size budget. `references/index.md` is generated from it (`python tools/references.py index`), and `tools/release.py check` fails on an unregistered or missing reference, a stale index, a profile list that disagrees with the registry, a file over the word budget, a profile without a source note, or a jurisdiction pack without a not-legal-advice statement.
- Added `jurisdictions/` (Brazil guidance moved from `brazilian-compliance.md` to `jurisdictions/brazil.md`, content unchanged) plus jurisdiction and copywriter-profile templates, so new markets and profiles are additive. No new legal content was written; other markets remain starting-point links in `sector-review.md`.
- **Evidence base.** New `references/evidence/` layer: `studies.json` is the source of truth for 21 research findings, each with an if/then rule, how to apply it, limits, caveats, evidence type, how far it transfers to commercial copy and a citation status (`supplied`, `index-checked`, `corrected`). Eight axis files are generated from it, alongside hand-written `principles.md` (four tiers of authority, precedence over integrity rules, citation legend, barrier-to-evidence map) and `review-checklist.md` (feeds the existing rubric dimensions; scoring and rubric 1.1.0 are unchanged). `release.py check` fails on a stale generated file, a study without limits, guarantee language, or example copy with concrete figures instead of placeholders.
- **Corrections to the supplied research base.** Verified against secondary indexes: Rains (2013) is "The Nature of Psychological Reactance Revisited: A Meta-Analytic Review", HCR 39(1), 47-73; O'Keefe & Hoeken (2021) is in Frontiers in Psychology 12:664160 with a different title (median effect about r = .10, prediction intervals include zero). Claims we could not support were left out: "up to twice as fast" for concreteness, "highly durable" narrative effects, the descriptive-over-injunctive norm ranking (the 1990 paper reports that either norm works when focused), the loss-aversion ratio attributed to the 1981 paper, and the 4-7 working-memory figure attributed to Sweller (1988). The "but you are free" technique is flagged as disputed, and "pennies-a-day" is flagged as needing the total price visible. Example copy that carried invented figures became placeholders.
- `briefing-dimensions.md` maps the 12 briefing dimensions to the strict brief fields and to conversation, without making every request a twelve-question interview. `jurisdictions/brazil.md` gains a copyright and originality section (Lei 9.610/98) and the CDC art. 37 pointer; both come from a supplied checklist and were not legally reviewed.
- Four profiles (Bencivenga, Bernbach, Schwab, Schwartz) now carry an explicit source note stating that no primary link is listed.
- `SKILL.md` is shorter: the reference list points to the generated index, and the validation and feedback sections are condensed with no change in rules.
- **Installers.** Remote installs now download the release archive pinned to their own version and verify its SHA-256 against `SHA256SUMS` instead of fetching the `main` branch; `--sha256` / `-Sha256` accepts an out-of-band hash. The release workflow publishes the archive, `SHA256SUMS` and both installers as a GitHub Release. **A release must exist for remote install to work.** `release.py check` fails if an installer pin differs from `VERSION`.
- **Rule catalog 1.1.0.** New review-level `number_word_signal` flags quantities written as words (for example "dois mil", "two thousand"), which the numeric-token check cannot compare. `health_signal` no longer fires on the Portuguese idiom "se trata de" / "trata-se". Existing logs recorded with catalog 1.0.0 are rejected by `summary` because the catalog hash changed; keep them separate.
- `contains()` raises `InputError` on an empty phrase instead of `IndexError`. The event-log lock file now records the owner PID and time so a stale lock is recognizable.
- Maintainer tooling: `pyproject.toml` (ruff, mypy, coverage), `requirements-dev.txt`, a `quality` CI job with an 85% coverage gate, and `push` CI limited to `main` plus pull requests to avoid duplicate runs.
- The original 1.4.0 changes retained the earlier schemas and exit codes. See the unreleased adjustments above for subsequent behavior and report changes. No live model benchmark was run; no performance claim is made.

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
