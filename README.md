# Copywriter Master

Copywriter Master is an instruction skill for AI assistants. It helps an assistant plan, write, and review commercial copy using audience research, clear strategy, human language, and evidence-aware claims. It is a knowledge package, not a standalone application. It does not guarantee conversion; outcomes also depend on the offer, audience, channel, and execution.

## What the skill does

1. **Diagnoses proportionally.** Uses available context and asks only questions that block an accurate or safe response.
2. **Follows the brief.** The user's requested format, amount, and scope take precedence. Open-ended ideation can include distinct options when useful.
3. **Uses research in the requested way.** It can synthesize research or use it to write copy, depending on the request.
4. **Writes clearly and humanely.** Uses concrete, natural language without invented evidence or generic hype.
5. **Provides specialist reference material.** Includes operational profiles of historical copywriters and framework authors, with caveats about attribution and evidence.

It is intended for commercial copy such as headlines, product pages, landing pages, ads, emails, CTAs, and sales scripts. It is not intended for noncommercial editing, proofreading, or translation.

## Skill contents

- skills/copywriter-master/SKILL.md — the assistant's core behavior and routing instructions.
- skills/copywriter-master/references/ — supporting knowledge to consult only when relevant: strategy, research, humanization, compliance, testing, source notes, and copywriter profiles.
- COPYWRITING_GUIDE.md — practical writing guidance.
- REFERENCES.md — complementary bibliography.

The skill should follow the user's language. Its reference materials are written in English to make the instructions easier for AI assistants to interpret.

## Add the skill to an assistant

The package contains no standalone application or runtime dependencies. Install the skill folder into a compatible assistant's skills directory. The included scripts automate copying that folder; they do not install software.

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
.\\install.ps1
~~~

Use -Dest, -Project, -DryRun, or -Uninstall for the equivalent options. If PowerShell blocks the script, run it with -ExecutionPolicy Bypass.

The scripts validate the skill identity, reject source and destination paths that overlap, stage a replacement before moving an existing installation, and restore the prior copy if activation fails. The PowerShell installer rejects paths that pass through symbolic links or junctions; use the physical path.

## Use and review

After installation, restart or open a new assistant session and try a representative commercial copy request. This can confirm that the skill loaded and followed that request's scope. It does not measure conversion or establish performance across audiences and channels.

## Scope and limitations

The skill supports editorial decisions; it does not replace product, legal, regulatory, or business approval. Factual proof and permission to make a regulated claim are separate requirements. Research, examples, historical profiles, and frameworks should be used within their stated evidence limits.

## License

Distributed under the Apache License 2.0. See LICENSE and NOTICE for details.
