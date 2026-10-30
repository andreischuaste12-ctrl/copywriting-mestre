# Reproducible Editorial Evaluation

This is a fixed **manual model-evaluation protocol**, not an automatic LLM judge or a conversion benchmark. The Python tool uses only the standard library (Python 3.10+); it never calls an API or generates copy. Repository tests verify the tools and package, not model behavior. No live model runs have been performed for this release and there is no claimed lift over a generic prompt.

## Compare three conditions

1. **Generic:** no Copywriter Master skill; use the exact case prompt with only this common instruction: “Complete the user's request accurately and follow its constraints.”
2. **Baseline:** load the pre-change skill from commit `3b22ed6` and use the same common instruction and case prompt.
3. **Candidate:** load the current complete skill folder and use the same common instruction and case prompt.

For the baseline, extract the historical package without changing the working checkout:

```sh
mkdir -p /tmp/copywriter-baseline
git archive 3b22ed6 skills/copywriter-master | tar -x -C /tmp/copywriter-baseline
```

Use the **same exact model/version, generation settings, tool access and context budget** for the three conditions. Start a clean session per case, load only the selected skill, and do not show expected responses, rubric anchors or previous outputs to the generating model. Allow relevant skill references consistently. Record any unavailable tools and platform defaults instead of guessing settings. If one condition cannot be loaded or the model version changes, label the comparison incomplete. Never pool different models as evidence of consistency.

Use at least three independent repetitions of every condition, with the same fixed cases. Rotate condition order across repetitions. Repeat the complete comparison separately for every model for which compatibility is claimed. These 15 cases are a regression sample, not representative evidence for all campaigns.

## Prepare a run

```sh
python3 tools/evaluate.py check
python3 tools/evaluate.py prepare --condition candidate --model 'provider/exact-model-version' --settings 'temperature=0.2; tools=none; fresh session per case' --repetition 1 --out /tmp/candidate-1.json
```

Replace the example model/settings with the actual environment. For `generic`, use `--condition generic`. For `baseline`, also pass `--skill-dir /tmp/copywriter-baseline/skills/copywriter-master`. Repeat with unique output paths and repetition numbers. Preparation fingerprints the entire selected skill package and fixed suite. It records repository HEAD as provenance; the skill hash also captures uncommitted package edits.

## Execute and review

1. Run each record's `prompt` in the specified condition; paste the actual unedited answer into `response`. Preserve essential clarification questions as the answer for missing-context cases. Do not fill with illustrative examples.
2. A human reviewer evaluates every answer against its brief and `expected` criteria using [the rubric](../skills/copywriter-master/references/quality-rubric.md). Fill all eight `scores` (integer 0–2), every `hard_failures` field (explicit boolean), and `review_note` with the evidence behind the judgment. Add a reviewer identifier in `reviewer`.
3. Blind the reviewer to condition labels when practical. Retain an ID mapping outside the blinded review. For disputed cases use a second reviewer and record the disagreement/resolution; never hide a safety failure in an average.
4. Keep identical case IDs, prompts, expectations and suite fingerprint. The tool refuses incomplete reviews, duplicated/omitted cases or modified prompts. It validates supplied scores; it does **not** detect false claims in prose or verify that a reviewer actually ran a model.
5. Generate a separate report:

```sh
python3 tools/evaluate.py score /tmp/candidate-1.json --out /tmp/candidate-1-report.json
```

Exit status: `0` all cases pass; `1` completed run has editorial failures; `2` invalid/incomplete input. Files are created exclusively to avoid overwriting evidence. Passing requires at least 13/16, no zero dimension, and no hard failure **for every case**. Retain failures and incomplete runs.

## Interpret the comparison

Report model/settings, skill and suite hashes, number of complete runs, per-case score/pass rate and hard failures, mean and range across repetitions, reviewer process, disagreements, and limitations. Compare each candidate case with its matching generic/baseline case; show regressions as well as gains. A mean increase with new hard failures is not an improvement. Do not label a compatible model “validated” from repository tests alone. Editorial ratings do not prove conversion; business outcomes need a separate controlled experiment with guardrails.

Keep raw runs and outputs in an authorized private location by default. Do not commit customer data or confidential model outputs. The fixtures are synthetic, and an empty run is not a benchmark result.
