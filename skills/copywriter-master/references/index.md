# Reference index

<!-- Generated from registry.json by `python tools/references.py index`. Do not edit by hand. -->

Load a reference only when its condition applies. Prefer the smallest set that resolves the task; use at most 2 copywriter profiles per task. SKILL.md and operating-protocol.md remain the authority on behavior.

## Protocol and quality gates

| Reference | Load when | Modes |
|---|---|---|
| [Operating protocol](operating-protocol.md) | Mode routing, ask-or-proceed decisions, and the default output contract. | Diagnose, Write, Review, Research, Optimize |
| [Quality rubric](quality-rubric.md) | Before delivering a draft, or when asked to audit or score copy. | Write, Review, Optimize |

## Strategy and craft

| Reference | Load when | Modes |
|---|---|---|
| [Copywriting strategy guide](copywriting-guide.md) | Choosing a structure by channel and awareness level; proof, price and guarantee copy. | Write, Review, Optimize |
| [Humanization](humanization.md) | Making copy specific and natural without simulated imperfections. | Write, Review |
| [Optimization and testing](optimization-and-testing.md) | Recommending tests, sample size, SRM, guardrails and diagnosis. | Optimize, Review |
| [Research and positioning](research-and-positioning.md) | Audience research, VoC, interviews, positioning and argument development. | Diagnose, Research, Write |

## Review processes

| Reference | Load when | Modes |
|---|---|---|
| [Claims matrix](claims-matrix.md) | Several benefits, numbers, comparisons, studies, guarantees or regulated claims. | Write, Review, Research |
| [Feedback loop](feedback-loop.md) | Feedback is given, or the user asks to record a case or result. | Diagnose, Write, Review, Research, Optimize |
| [Local validation contract](local-validation.md) | Machine-readable output or the local validator is requested. | Write, Review |

## Sector and market review

| Reference | Load when | Modes |
|---|---|---|
| [Sector and market review](sector-review.md) | The brief depends on a sector or market; per-market starting points for review. | Write, Review |

## Jurisdiction packs

| Reference | Load when | Modes |
|---|---|---|
| [Brazil advertising and data notes](jurisdictions/brazil.md) | Brazil applies: consumer advertising, health/supplements, privacy, testimonials. | Write, Review |

## Copywriter and framework profiles

| Reference | Load when | Modes |
|---|---|---|
| [Copywriter profile index](copywriters/index.md) | A style or technique is requested, or a barrier maps to a known technique. | Write, Review, Optimize |

## Examples

| Reference | Load when | Modes |
|---|---|---|
| [Application cases](application-cases.md) | Examples of scope fidelity, research, integrity and diagnosis; not performance evidence. | Diagnose, Write, Review, Research, Optimize |
| [Output examples](output-examples.md) | The format is unfamiliar or an example would resolve ambiguity. | Write, Review, Optimize |

## Sources

| Reference | Load when | Modes |
|---|---|---|
| [Source notes](sources.md) | Before repeating a historical attribution, date or effectiveness claim. | Write, Research, Review |

## Individual profiles

20 profiles live in `copywriters/`. Open [copywriters/index.md](copywriters/index.md) first and then only the one or two profiles it selects.

## For maintainers

Not loaded during normal tasks. Adding a reference means: copy a template, register it in `registry.json`, then run `python tools/references.py index` and `python tools/release.py check`.

- [Copywriter profile template](copywriters/_template.md)
- [Jurisdiction pack template](jurisdictions/_template.md)
