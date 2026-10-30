# Application Cases

These examples illustrate how to follow user intent and evidence limits. They are not performance data or fixed response templates.

## A. One CTA, strict character limit

**Request:** “Give me one CTA, no more than 18 characters, no explanation.”

**Good response:** Provide one CTA and count the characters internally. Do not add multiple alternatives, strategy notes, or a test plan.

**Principle:** Explicit format and quantity take precedence over open-ideation defaults.

## B. Research supplied with a copy request

**Request:** “Use these interview notes to write one ad.”

**Good response:** Extract only the relevant supported language and insight, then write the ad. Keep a quote literal and contextualized; label an inferred audience desire as a hypothesis. Do not replace the requested ad with a research summary.

**Principle:** Distinguish “organize this research” from “use this research to write.”

## C. Research-only request

**Request:** “Organize this study into audience problems, desires, and objections.”

**Good response:** Synthesize the evidence, cite the source passages, distinguish observation from interpretation, and list gaps. Do not draft campaign copy unless requested.

## D. Not enough customer language

**Input:** Four relevant customer quotes.

**Good response:** Use at most those four quotes. Do not duplicate them to meet a profile's suggested count. If no VoC exists, ask for a source or label proposed wording as an editorial hypothesis.

## E. Maintenance notice

**Request:** “Make this maintenance notice clearer.”

**Good response:** State when the service will be unavailable, what users can expect, and where to get help. Do not turn the notice into a sales campaign.

**Principle:** Commercial-copy triggers must not capture routine functional writing.

## F. Regulated claim with evidence but no permission

**Input:** A study suggests a supplement ingredient may affect a health outcome, but there is no confirmation that the claim is permitted for this product and market.

**Good response:** Do not draft that health promise, including a softened version. Ask for the approved claim and current label or limit copy to neutral, verifiable product attributes. Route uncertainty for regulatory review.

**Principle:** Evidence and authorization are separate.

## G. Funnel signal with a technical failure

**Input:** Many checkout attempts fail with a payment-provider error.

**Good response:** Recommend investigating error codes, provider status, and the technical path first. Do not assume that users need more reassurance copy.

**Principle:** Behavioral signals generate hypotheses; technical failures need technical diagnosis.

## H. A/B split with a small count difference

**Input:** Assignment is 51/49 among 100 users.

**Good response:** Do not reject the experiment on the percentage alone. Compare observed and expected counts with an appropriate, preselected SRM check. Investigate a statistical alert before interpreting results; the alert does not identify the cause.

**Principle:** Sample-ratio assessment depends on counts and a statistical criterion, not a universal percentage cutoff.

## I. Requested language

Respond in the user's language unless they request another language. The repository and reference content being in English does not require an English response to a user who writes in another language.

For complete synthetic good/bad outputs, see [output-examples.md](output-examples.md). Apply the shared [quality rubric](quality-rubric.md) before delivery.
