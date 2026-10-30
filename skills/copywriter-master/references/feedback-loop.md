# Feedback and Versioned Learning

This package has no telemetry, background storage, or automatic model training. It can use feedback present in the current conversation. Persistent records require the user's explicit request and an available destination; say when no storage tool exists. Do not interrupt a strict final-copy format for a feedback question.

## Revision loop

1. Capture a concrete problem: unclear offer, wrong voice, unsupported promise, wrong action, or channel mismatch.
2. Connect it to a brief fact or user preference. A preference is not evidence of conversion.
3. Revise the smallest affected part, preserve terms, and apply the rubric again.
4. For a request to record results, save a redacted case using the template below. Never store raw personal identifiers, private customer quotes, or secret business data in a public repository.
5. Propose a reusable rule only after checking counterexamples and scope. Re-run the fixed evaluation cases and keep negative/inconclusive findings.

## Case record template

- Case ID / date / skill version / model identifier:
- Mode / channel / redacted audience and objective:
- Supported brief and source IDs (authorized excerpts only):
- Prior response and concrete feedback (redacted):
- Revision and reason:
- Rubric scores / hard failures / reviewer:
- Result type: editorial preference, usability observation, or experiment:
- Observed outcome / denominator / period / guardrails / limitations, if measured:
- Decision / unresolved question:
- User authorization and private storage destination, if saved:

Do not call a preference a performance win. Do not generalize a one-off result to all audiences or models.

## Release rules

Use semantic versions in SKILL.md metadata and the root VERSION file. Patch: clarification without intended behavioral change. Minor: compatible new modes, examples, or quality checks. Major: incompatible routing or output contract. Record behavioral changes and validation in CHANGELOG.md. Keep the prompt/skill fingerprint, cases, model/settings, and outputs with each benchmark run. The test corpus is not itself a benchmark result.
