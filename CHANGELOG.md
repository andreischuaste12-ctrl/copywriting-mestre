# Changelog

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
