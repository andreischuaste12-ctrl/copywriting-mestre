# Maintenance and release policy

Andrei Schuaste is the project author and copyright holder under Apache-2.0. Maintainers must preserve LICENSE and NOTICE in the installable package. The Apache legal terms are not an application compatibility guarantee.

## Version boundaries

| Component | Current version | Breaking change examples |
|---|---|---|
| Skill behavior | Release 1.3.1; contract 1.0 | Incompatible mode routing, mandatory wrappers for previously copy-only requests |
| Brief/output | Schema contract 1.0 | Required new fields, removed enums, changed field meaning |
| Reports/events/batches | Contract 1.0 | Removed fields, changed status/exit meaning, altered event denominator |
| Rule catalog | 1.0.0 | Removed/renamed finding codes or materially changed rule meaning |
| Editorial rubric | 1.1.0 | Changed anchors, weights, threshold or interpretation |

Use a patch for compatible fixes/documentation; a minor for additive capabilities; a major for incompatible public behavior. A newly blocking rule or changed limit needs an explicit impact note and migration examples even when input fields stay identical. Keep the version 1.2 validator wrapper and exit codes during the 1.x series. Additive report fields are allowed; strict input schemas need a new schema version for new fields. Do not reuse a version or silently reinterpret old logs. No calendar support duration is promised.

## Release checklist

1. Review behavior, rules, schemas and examples together. Identify breaking changes and migration impact. Update VERSION, skill metadata, README and CHANGELOG consistently.
2. Preserve the separate rubric version unless editorial scoring changes; preserve old raw benchmark runs. Compare completed runs only with matching model/settings and fixed suite. Do not label fixtures as real campaigns.
3. Run `python tools/release.py check`, the unit suite, and Bash syntax checks. Inspect native Linux/macOS/Windows CI results for the exact commit. Installer checks must include licenses, schemas, project destinations, update and uninstall.
4. Run `python tools/release.py build --out ./dist --expected-version v1.3.1` into a new directory, then `python tools/release.py verify --directory ./dist`. The archive is reproducible for identical skill bytes and compression runtime; checksums verify every included file.
5. Review package contents, changelog, risk-regression results, known limitations and live benchmark status. Tag only the reviewed commit with the matching version. The tag-triggered workflow builds and uploads a workflow artifact; it does not create a GitHub Release or publish a service automatically.
6. After release, retain the archive/manifest and commit identity, link actual CI results, and record regressions or rollback decisions. Revert the affected code/version through a reviewed change; do not overwrite previous artifacts.

## Real case intake and regressions

Real-world cases require permission to use the supplied material, removal of personal/confidential data, source traceability, and an agreed private/public destination. Use [the feedback template](../skills/copywriter-master/references/feedback-loop.md). Record sector, market, channel, language, brief and output fingerprints, expected failure codes, actual correction and reviewer. Label evidence as synthetic, editorial observation or measured experiment. Preserve conflicting findings and counterexamples.

A redacted real example still does not prove conversion lift. Campaign metrics need denominator, timeframe, population, instrumentation, guardrails and an appropriate comparison. Do not commit raw customer briefs or unverified legal claims. The current sector corpus remains synthetic until authorized cases are actually supplied.

## Failure triage

Categorize reports using stable rule categories: format, audience, offer, CTA, evidence, compliance, privacy and clarity. Prioritize critical unsupported/held claims and exposed identifiers, then high-impact offer/action failures. Distinguish a false-positive literal match from a verified policy issue. For an incident, retain version/hash, redacted reproduction, actual finding and expected behavior; add a regression before changing the rule. A human-review requirement is a design policy, not an incident.
