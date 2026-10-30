"""Render validation and aggregate reports without including draft or source text."""
import html
import json


def render(data, format='json'):
    if format == 'json':
        return json.dumps(data, ensure_ascii=False, indent=2) + '\n'
    if 'findings' in data:
        lines = ['# Copy validation', '', f'Automatic checks: **{data["automated_checks"]}**',
                 f'Disposition: **{data["disposition"]}**', '',
                 '| Priority | Category | Code | Next action |', '|---|---|---|---|']
        for row in data['findings']:
            lines.append(f'| {row["priority"]} | {row["category"]} | {row["code"]} | {row["remediation"]} |')
        lines += ['', 'Passing deterministic checks is not factual verification or legal approval.']
    else:
        lines = ['# Local validation activity', '', f'Events: {data["event_count"]}',
                 f'Blocked: {data["blocked_count"]}', f'Block rate: {data["block_rate"]}',
                 f'Human-review-required rate: {data["human_review_required_rate"]}', '',
                 '| Failure/review code | Occurrences |', '|---|---|']
        lines.extend(f'| {key} | {value} |' for key, value in sorted(data['finding_counts'].items()))
        lines += ['', 'Counts describe logged validation calls, including retries. Human review is required by design; this is not a measured editorial defect rate or conversion result.']
    markdown = '\n'.join(lines) + '\n'
    if format == 'markdown':
        return markdown
    if format == 'html':
        return '<!doctype html><html lang="en"><meta charset="utf-8"><title>Copywriter Master report</title><style>body{font:16px system-ui;max-width:1000px;margin:40px auto;padding:0 20px}pre{white-space:pre-wrap;line-height:1.6}</style><body><pre>' + html.escape(markdown) + '</pre></body></html>\n'
    raise ValueError('Unsupported report format')
