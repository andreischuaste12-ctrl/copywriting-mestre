"""Explicit local event logging; no raw briefs, copy, source text, identifiers or network."""
from collections import Counter
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import uuid

from .validation import InputError, load_json, ROOT, validate_structure, fingerprint


def event_for(report):
    return {'schema_version': '1.0', 'event_id': uuid.uuid4().hex,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            **{k: report[k] for k in ('validator_version', 'runtime_contract_version', 'rule_catalog_version',
                                     'rule_catalog_sha256', 'brief_sha256', 'output_sha256',
                                     'automated_checks', 'human_review_required')},
            'finding_counts': dict(Counter(f['code'] for f in report['findings'])),
            'category_counts': dict(Counter(f['category'] for f in report['findings']))}


def append_events(path, reports):
    events = [event_for(report) for report in reports]
    for event in events:
        validate_structure(event, 'event')
    path = Path(path)
    lock = path.with_name(path.name + '.lock')
    # Exclusive creation rejects simultaneous writers; never delete a lock owned by another writer.
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise InputError('Event log is locked by another writer; retry after it finishes. Inspect a stale lock manually.') from exc
    try:
        os.close(fd)
        if path.exists():
            # Refuse to append to a brief, draft, report, corrupt log or incompatible catalog.
            summarize(path)
        log_fd = os.open(path, os.O_CREAT | os.O_APPEND | os.O_WRONLY, 0o600)
        with os.fdopen(log_fd, 'a', encoding='utf-8', newline='\n') as stream:
            for event in events:
                stream.write(json.dumps(event, ensure_ascii=False, separators=(',', ':')) + '\n')
    finally:
        lock.unlink()


def summarize(path):
    events = []
    seen = set()
    catalog = load_json(ROOT / 'skills/copywriter-master/rules/validation.json')
    catalog_hash = fingerprint(catalog)
    rule_records = {r['code']: r for r in catalog['rules']}
    rules = {code: r['category'] for code, r in rule_records.items()}
    with Path(path).open(encoding='utf-8') as stream:
        for number, line in enumerate(stream, 1):
            if not line.strip():
                continue
            try:
                # Reuse duplicate-key rejection without putting private input in diagnostics.
                def unique(items):
                    result = {}
                    for k, v in items:
                        if k in result:
                            raise InputError('Duplicate event key')
                        result[k] = v
                    return result
                event = json.loads(line, object_pairs_hook=unique)
                validate_structure(event, 'event')
                if event['event_id'] in seen:
                    raise InputError('Duplicate event ID')
                seen.add(event['event_id'])
                if event['rule_catalog_sha256'] != catalog_hash:
                    raise InputError('Event uses a different rule catalog')
                timestamp = datetime.fromisoformat(event['timestamp'])
                if timestamp.tzinfo is None:
                    raise InputError('Event timestamp must include timezone')
                if event['finding_counts'].get('semantic_review') != 1:
                    raise InputError('Event must retain semantic review')
                if set(event['finding_counts']) - set(rules):
                    raise InputError('Unknown rule code; summarize with the matching runtime/rule catalog')
                expected = Counter()
                for code, count in event['finding_counts'].items():
                    expected[rules[code]] += count
                has_error = any(rule_records[code]['severity'] == 'error' for code in event['finding_counts'])
                if has_error != (event['automated_checks'] == 'failed'):
                    raise InputError('Event status disagrees with findings')
                if dict(expected) != event['category_counts']:
                    raise InputError('Event category counts do not match rule counts')
            except (ValueError, TypeError) as exc:
                raise InputError(f'Invalid event at line {number}; preserve the original file and correct the import.') from exc
            events.append(event)
    findings, categories = Counter(), Counter()
    for event in events:
        findings.update(event['finding_counts'])
        categories.update(event['category_counts'])
    n = len(events)
    blocked = sum(e['automated_checks'] == 'failed' for e in events)
    return {'schema_version': '1.0', 'event_count': n, 'blocked_count': blocked,
            'block_rate': blocked / n if n else None,
            'human_review_required_rate': 1.0 if n else None,
            'finding_counts': dict(findings), 'category_counts': dict(categories),
            'populations': sorted({(e['validator_version'] + '/' + e['rule_catalog_version']) for e in events}),
            'measurement_scope': 'logged validation calls, including retries; not model or campaign performance'}
