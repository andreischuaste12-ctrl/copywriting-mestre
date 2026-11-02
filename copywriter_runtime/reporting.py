"""Render validation and aggregate reports without including draft or source text."""
import html
import json


def render(data, format='json'):
    if format == 'json':
        return json.dumps(data, ensure_ascii=False, indent=2) + '\n'
    if 'findings' in data:
        title = 'Copy validation'
        details = [('Automatic checks', data['automated_checks']), ('Disposition', data['disposition'])]
        headers = ['Item', 'Priority', 'Category', 'Code', 'Finding', 'Next action']
        rows = [[row.get('item_id', '—'), row['priority'], row['category'], row['code'],
                 row['message'], row['remediation']] for row in data['findings']]
        note = 'Passing deterministic checks is not factual verification or legal approval.'
    else:
        title = 'Local validation activity'
        details = [('Events', data['event_count']), ('Blocked', data['blocked_count']),
                   ('Block rate', data['block_rate']), ('Human-review-required rate', data['human_review_required_rate'])]
        headers = ['Failure/review code', 'Occurrences']
        rows = list(sorted(data['finding_counts'].items()))
        note = ('Counts describe logged validation calls, including retries. Human review is required by design; '
                'this is not a measured editorial defect rate or conversion result.')
    if format == 'markdown':
        def cell(value):
            return str(value).replace('\\', '\\\\').replace('|', r'\|').replace('\n', ' ').replace('\r', ' ')
        lines = [f'# {title}', ''] + [f'{label}: {cell(value)}' for label, value in details] + ['']
        lines += ['| ' + ' | '.join(headers) + ' |', '|' + '|'.join(['---'] * len(headers)) + '|']
        lines += ['| ' + ' | '.join(cell(value) for value in row) + ' |' for row in rows]
        return '\n'.join(lines + ['', note]) + '\n'
    if format == 'html':
        def escape(value):
            return html.escape(str(value), quote=True)
        detail_html = ''.join(f'<p><strong>{escape(label)}:</strong> {escape(value)}</p>' for label, value in details)
        header_html = ''.join(f'<th scope="col">{escape(value)}</th>' for value in headers)
        row_html = ''.join('<tr>' + ''.join(f'<td>{escape(value)}</td>' for value in row) + '</tr>' for row in rows)
        return ('<!doctype html><html lang="en"><head><meta charset="utf-8"><title>' + escape(title) + '</title>'
                '<style>body{font:16px system-ui;max-width:1200px;margin:40px auto;padding:0 20px}'
                'table{border-collapse:collapse;width:100%}th,td{border:1px solid #bbb;padding:8px;text-align:left;'
                'vertical-align:top}th{background:#eee}</style></head><body><h1>' + escape(title) + '</h1>'
                + detail_html + '<table><thead><tr>' + header_html + '</tr></thead><tbody>' + row_html
                + '</tbody></table><p>' + escape(note) + '</p></body></html>\n')
    raise ValueError('Unsupported report format')
