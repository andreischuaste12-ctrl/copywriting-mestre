# Compatibility and support boundaries

A directory copy, a host loading a skill, and a model following instructions are different claims. This project currently has automated filesystem/contract tests, not a completed cross-client or cross-model behavior benchmark.

| Target | Integration route | What is checked | What remains unverified |
|---|---|---|---|
| Claude Code-style clients | `.claude/skills/copywriter-master` | Project installation, update, dry run, identity and package files | Current client discovery and live model behavior |
| Codex/Agents-style clients | `.agents/skills/copywriter-master` | Same filesystem checks | Current client discovery and live model behavior |
| OpenAI GPT/ChatGPT configurations | Explicitly load instructions and relevant references using the host's supported mechanism | Portable Markdown/JSON files | Automatic discovery, feature parity, model quality; this is not a one-click GPT import |
| Other/local assistants | Explicit skill folder or host adapter | Strict schemas and local validator | Context budget, reference loading and instruction priority in that host |
| Local Python integrations | `copywriter_runtime.validate_copy` | Python 3.10 contract/regression tests | Semantic truth, actual prose language, current legal permission |

CI defines tests for Linux, macOS and Windows, with a separate native PowerShell installation job on Windows. A configured job is not a successful run: consult the GitHub Actions result for the exact commit. Local Linux verification does not certify Windows or macOS execution. WSL follows the Linux shell path but does not have a separate live-host certification.

Both default project paths are tested with `--project` in a temporary project. Custom `--dest` installation remains available. The v1.2 `tools/validate_copy.py` entrypoint and exit codes remain supported. Python tooling requires the optional dependency file; the instruction skill has no runtime dependencies.

Before marking a host/model as behavior-tested, record client version, model identifier, date, OS, skill fingerprint, discovery method, relevant reference loading, fixed-case results and limitations in an authorized record. Do not infer this status from an installer success or synthetic fixtures.

For migration/version rules and support policy, see [maintenance](MAINTENANCE.md). There are no promised future support windows or guarantees for changing third-party hosts.
