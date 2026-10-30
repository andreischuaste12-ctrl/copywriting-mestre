# Local observability

Nothing is logged by default. Opt in for a single command by passing a local path:

```sh
python tools/copywriter.py validate --brief examples/validation/brief.pt-BR.json --draft examples/validation/output.pt-BR.json --log ./events.jsonl
python tools/copywriter.py summary --log ./events.jsonl --format markdown
python tools/copywriter.py summary --log ./events.jsonl --format html --out ./activity.html
```

The JSONL event schema is installed in `schemas/event.schema.json`. Each event records a random event ID, UTC timestamp, runtime/rule versions and hashes, brief/output fingerprints, automatic status, human-review requirement, and counts by finding code/category. It deliberately omits raw copy, source text, names, emails, brief IDs, item IDs, file paths and user identifiers. Do not append additional business/customer data to this schema.

Logs stay at the path you provide; there is no upload, automatic retention policy, training, hidden cache or cross-session memory. The owner chooses access, retention and deletion. A new log is created with owner-only mode on systems supporting POSIX permission bits; use suitable Windows folder ACLs. Existing files must already be valid compatible event logs (or empty); the logger refuses to append to a brief, draft, report or corrupted file. The `.lock` file rejects simultaneous writers immediately rather than interleaving JSON. If a process crashes, inspect the stale lock before deleting it; another writer's lock is never removed automatically.

Summary rejects malformed/duplicate events, mismatched status/category counts and incompatible rule catalogs. Duplicate **event IDs** are rejected. A repeated validation of the same brief/output has a new event ID and counts as another call. Population/version labels and hashes preserve context, but events are not signed or proof that their inputs were truthful.

Metrics use **logged validation calls** as the denominator, including retries. Block rate counts calls with automatic failures. Human-review-required rate is 100% for nonempty valid logs because that is the validator's policy; it is not measured model uncertainty or a failure rate. An empty log has null rates. Counts by rule/category include review signals as well as errors. These numbers do not measure CTR, conversion, customer retention or reviewer work time.

Reports are emitted before logging. If writing a report succeeds but logging fails, the command returns exit `2`; keep the saved report and repair logging rather than assuming the operation was atomic across two files. Batch input errors are detected before report creation; a later logging error may leave a completed batch. No malformed-input events or raw errors are automatically stored.
