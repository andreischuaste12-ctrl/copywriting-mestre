# Start in 15 minutes

Use Python 3.10+ from the repository root in your virtual environment. No API key or model service is required. The fixtures are synthetic and do not establish model performance.

```sh
python -m pip install -r requirements-validation.txt
python tools/copywriter.py init --example en-US --dest ./first-case
python tools/copywriter.py validate --brief ./first-case/brief.json --draft ./first-case/output.json --format markdown
```

The new directory contains `brief.json` and `output.json`. Existing folders are preserved. Expected result: deterministic checks pass and human review remains required. The English sample is one short CTA for a confirmed free trial. Append an unsupported `50%` discount to the output and rerun: it should be blocked for an unprovided number and length. Restore the draft without changing trusted constraints to obtain a pass.

The brief owner confirms audience, offer, terms, CTA and evidence. The generating assistant supplies output matching the schema. This CLI reviews existing output; it does not generate copy or confirm legal permission. `--format json`, `markdown` and `html` export local reports; `--out` requires a new file. Exit `0` means automatic checks passed, `1` means copy violations, and `2` means invalid input or a tool/file error.

Validate the synthetic sector examples in one command:

```sh
python tools/copywriter.py batch --manifest examples/sectors/batch.json --out-dir ./sector-reports
```

For explicit local event logging, add `--log ./events.jsonl` to validation or batch commands. Then use `python tools/copywriter.py summary --log ./events.jsonl --format markdown`. Logging is off otherwise. See [observability](OBSERVABILITY.md), [compatibility](COMPATIBILITY.md), and [maintenance](MAINTENANCE.md) for limits and evidence requirements. Portuguese users can follow the [Portuguese walkthrough](QUICKSTART.pt-BR.md).
