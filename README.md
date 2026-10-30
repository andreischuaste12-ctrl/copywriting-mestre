# Copywriter Master

Copywriter Master is an instruction skill for AI assistants. It helps an assistant plan, write, and review commercial copy using audience research, clear strategy, human language, and evidence-aware claims. It is an instruction package with an optional local validator for structured briefs and draft outputs. It does not guarantee conversion; outcomes also depend on the offer, audience, channel, and execution.

## Start here

Version **1.3.0** · **Apache-2.0**.

Follow the 15-minute [Portuguese quickstart](docs/QUICKSTART.pt-BR.md) or [English quickstart](docs/QUICKSTART.en.md). For supported integration paths and what has actually been tested, see the [compatibility matrix](docs/COMPATIBILITY.md). Filesystem installation checks do not establish that a live model loaded or followed the skill.

```sh
python -m pip install -r requirements-validation.txt
python tools/copywriter.py init --example pt-BR --dest ./first-case
python tools/copywriter.py validate --brief ./first-case/brief.json --draft ./first-case/output.json --format markdown
```

The examples are synthetic and run without an API key. The CLI validates existing copy; generation stays with the assistant of your choice. Original briefs and registered source references remain the responsibility of their owner.

## What the skill does

1. **Diagnoses proportionally.** Uses available context and asks only questions that block an accurate or safe response.
2. **Follows the brief.** The user's requested format, amount, and scope take precedence. Open-ended ideation can include distinct options when useful.
3. **Uses research in the requested way.** It can synthesize research or use it to write copy, depending on the request.
4. **Writes clearly and humanely.** Uses concrete, natural language without invented evidence or generic hype.
5. **Checks editorial quality.** Applies eight anchored criteria and blocks unsupported claims, unconfirmed regulated promises, invented scarcity, changed terms, privacy violations, and explicit scope failures.
6. **Provides specialist reference material.** Includes operational profiles of historical copywriters and framework authors, with caveats about attribution and evidence.

It is intended for commercial copy such as headlines, product pages, landing pages, ads, emails, CTAs, and sales scripts. It is not intended for noncommercial editing, proofreading, or translation.

## Skill contents

- skills/copywriter-master/SKILL.md — the assistant's core behavior and routing instructions.
- skills/copywriter-master/references/ — supporting knowledge to consult only when relevant: strategy, research, humanization, compliance, testing, source notes, and copywriter profiles.
- [Output examples](skills/copywriter-master/references/output-examples.md) — ten complete synthetic good/bad examples for ads, headlines, landing sections, emails, CTAs, review, research, regulated claims, subscriptions, and premium offers.
- [Operating protocol](skills/copywriter-master/references/operating-protocol.md) — mode routing, decision tree, and proportional output contract.
- [Quality rubric](skills/copywriter-master/references/quality-rubric.md) — eight anchored dimensions, a 13/16 gate, and hard failures.
- [Evaluation protocol](evaluation/README.md) — 15 fixed cases, manual benchmark workflow, and scoring tools.
- [Changelog](CHANGELOG.md) and VERSION — versioned behavior and release history.
- COPYWRITING_GUIDE.md — practical writing guidance.
- REFERENCES.md — complementary bibliography.

The skill should follow the user's language. Its reference materials are written in English to make the instructions easier for AI assistants to interpret.

## Add the skill to an assistant

The instruction skill has no runtime dependencies. The optional local validation CLI separately requires Python 3.10+ and jsonschema. Install the skill folder into a compatible assistant's skills directory. The included scripts automate copying that folder; they do not install software.

### macOS, Linux, and WSL

Run directly from the repository:

~~~sh
./install.sh
~~~

Or install from a local copy to a chosen directory:

~~~sh
./install.sh --dest /path/to/skills
~~~

Options:

| Purpose | Option |
|---|---|
| Install to default user directories | ./install.sh |
| Install to a chosen directory | ./install.sh --dest PATH |
| Install to the current project | ./install.sh --project |
| Preview without changing files | ./install.sh --dry-run |
| Remove this skill | ./install.sh --uninstall |

### Windows PowerShell

Run install.ps1 from the repository folder:

~~~powershell
.\install.ps1
~~~

Use -Dest, -Project, -DryRun, or -Uninstall for the equivalent options. If PowerShell blocks the script, run it with -ExecutionPolicy Bypass.

The scripts validate the skill identity, reject source and destination paths that overlap, stage a replacement before moving an existing installation, and restore the prior copy if activation fails. The PowerShell installer rejects paths that pass through symbolic links or junctions; use the physical path.

## Practical use

Restart or open a new assistant session after installation. The assistant follows your language; the package being in English does not force English output.

| Mode | Example request |
|---|---|
| Diagnose | “Given this brief, identify the main decision barrier and missing evidence. Do not write copy yet.” |
| Write | “Write one landing page section for this audience, using only these product facts. CTA: book a demo.” |
| Review | “Review this sales email, list factual risks, and provide one rewrite preserving the exact price and terms.” |
| Research | “Organize these interviews into problems, desires, and objections. Cite source IDs; do not write ads.” |
| Optimize CTA / offer | “Give one Portuguese CTA, at most 18 characters, for a confirmed free trial. No explanation.” |

### A useful brief

> Write one Portuguese ad, at most 160 characters, with no explanation. Turno is a weekly calendar for independent tutors with SMS reminders. CTA opens a demonstration. Use only these facts; there is no earnings evidence or deadline.

An appropriate synthetic output is:

> Organize suas aulas da semana e envie lembretes por SMS com o Turno. Veja a demonstração.

A weak prompt is “Make my product irresistible.” It omits the product, audience, channel and action. A bad output would be “Double your income in 7 days. Last free seats!” because it invents results, scarcity and free access. These are teaching examples, not measured performance results.

### When the assistant asks questions

The assistant asks a concise bundled question when a missing product identity, conflicting price, or required regulated permission blocks useful work. It proceeds when context is adequate, chooses a reasonable tone if none is supplied, and does not demand testimonials to fill a template. If you request no questions, it uses verified facts and holds unsupported promises. It never guesses material terms or permission.

Open-ended strategy can use Brief, Audience, Problem, Offer, Proof, CTA, Risks, and Final copy. A request for one CTA receives one CTA, with no audit or feedback questionnaire. Research-only work receives findings and next decisions rather than unsolicited sales copy.

## Optional local runtime (1.3)

Check structured draft copy against a human-maintained brief without calling an AI service. The validator checks JSON schemas, item counts and limits, exact required terms, accepted CTAs, numeric tokens and registered claim references. It blocks detected violations and always retains human review for factual meaning and legal permission.

```sh
python -m pip install -r requirements-validation.txt
python tools/validate_copy.py --brief examples/validation/brief.pt-BR.json --draft examples/validation/output.pt-BR.json
```

Try the blocked example by replacing the draft path with `examples/validation/output.blocked.pt-BR.json`. For an English CTA, use `brief.en-US.json` and `output.en-US.json` from the same directory. Examples are synthetic. Add `--out /path/to/new-report.json` to save a report; existing files are preserved.

Exit `0`: automatic checks passed, human review required. Exit `1`: detected copy violations. Exit `2`: invalid input or tool error. A passing result does not prove that a claim is true, complete, or legally authorized. Sources are registered references, not verified evidence. The validator does not repair drafts or generate copy.

Read the [contract, fields and limitations](skills/copywriter-master/references/local-validation.md). The [brief](skills/copywriter-master/schemas/brief.schema.json) and [output](skills/copywriter-master/schemas/output.schema.json) schemas accompany installed skills. Use structured mode only when requested; ordinary chat requests keep their format.

### Batch review and local activity reports

```sh
python tools/copywriter.py batch --manifest examples/sectors/batch.json --out-dir ./sector-reports
python tools/copywriter.py validate --brief examples/validation/brief.pt-BR.json --draft examples/validation/output.pt-BR.json --log ./events.jsonl
python tools/copywriter.py summary --log ./events.jsonl --format html --out ./activity.html
```

Batch review exports JSON and Markdown to a new directory. Six [sector examples](examples/sectors/batch.json) cover SaaS/B2B, e-commerce, education, fintech, health and services/SMS across Portuguese, English and Spanish. All are synthetic fixtures; they do not prove live campaign quality. [Sector/market worksheets](skills/copywriter-master/references/sector-review.md) organize required human review without claiming a legal clearance engine.

Logging is off unless `--log` is supplied. Events omit raw briefs, copy and source text. The local activity summary reports rule/category counts and block frequency; retries count as calls, and human review is required by design. See [observability](docs/OBSERVABILITY.md) for schemas, locking and metric limits. The [architecture](docs/ARCHITECTURE.md) separates behavior, knowledge, contracts, rules and execution and documents the public local Python API.

## Quality checks and benchmark status

Before delivery, the skill applies the [editorial rubric](skills/copywriter-master/references/quality-rubric.md): audience fit, offer clarity, evidence, CTA, compliance, channel fit, readability, and emotional relevance. Each dimension scores 0–2; readiness requires at least 13/16, no zero, and no hard failure. This is a revision rule, not proof of improved conversions. Self-ratings are not independent evaluation.

Check the package and tools locally with Python 3.10+ and Bash:

```sh
python3 -m pip install -r requirements-validation.txt
python3 tools/release.py check
python3 -m unittest discover -s tests -v
bash -n install.sh
```

GitHub Actions defines Python validation checks on Linux, macOS and Windows, plus a Windows PowerShell installer check. Repository tests exercise package integrity, scoring gates, installation and deterministic copy violations; they do not measure generated model quality. There are **no completed live model benchmarks or conversion results for this release**. Follow the [evaluation protocol](evaluation/README.md) to compare generic, baseline and candidate conditions using the same model/settings, fresh sessions, three or more repetitions, and human review. Compatibility across models remains unmeasured until those comparisons are run.

### Releases and benchmark comparison

The [maintenance policy](docs/MAINTENANCE.md) defines breaking changes, version boundaries, migration and the release checklist. `python tools/release.py build --out ./dist --expected-version v1.3.0` produces an installable skill ZIP, file manifest and SHA256SUMS without publishing. `python tools/release.py verify --directory ./dist` checks archive and individual files. Matching-version tags trigger a test/build workflow and a downloadable workflow artifact; they do not automatically publish a GitHub Release.

Completed human-reviewed runs can be compared with `python tools/evaluate.py compare run1.json run2.json --out comparison.html --format html`. The report is incomplete until generic/baseline/candidate have matching sets of at least three repetitions, the same model/settings, and consistent skill fingerprints per condition. It displays per-case means, ranges, pass rates and hard failures. No completed benchmark data is bundled or invented.

## Feedback and evolution

Give concrete feedback such as “the offer is unclear,” “this phrase changes the guarantee,” or “keep the tone more direct.” The skill uses feedback available in the current conversation. It saves a case externally only when you request it and has no telemetry, automatic training or guaranteed memory between sessions. Use the [case-record template](skills/copywriter-master/references/feedback-loop.md) for explicitly requested, redacted records. The [changelog](CHANGELOG.md) records behavioral changes; version metadata and benchmark fingerprints identify what was tested.

## Scope and limitations

The skill supports editorial decisions; it does not replace product, legal, regulatory, or business approval. Factual proof and permission to make a regulated claim are separate requirements. Research, examples, historical profiles, and frameworks should be used within their stated evidence limits.

## License

Copyright 2026 **Andrei Schuaste**, project author and copyright holder. Distributed under the [Apache License 2.0](LICENSE); see [NOTICE](NOTICE) for attribution. The same LICENSE and NOTICE are included in the installable skill folder, so both scripted and manual folder installations retain them.

Third-party books, campaigns, names, and trademarks retain their respective owners and rights. The project license covers this project's original material; referencing a work does not license that original work or imply endorsement.
