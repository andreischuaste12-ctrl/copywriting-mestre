# Optimization and Testing

Use this reference when proposing a test, reading results, or diagnosing underperformance. It supports disciplined decision-making; it does not promise that a copy change will improve results.

## Experiment workflow

1. **Start with an observed barrier.** State what evidence suggests a problem with relevance, comprehension, proof, trust, or convenience.
2. **Write one hypothesis.** “If we clarify compatibility beside the CTA, fewer visitors may abandon because of uncertainty.” Keep one primary change per comparison.
3. **Choose an outcome and guardrails.** Use a business outcome such as qualified leads, purchases, margin, returns, cancellations, or complaints. CTR alone can rise while business quality falls.
4. **Plan before launch.** Define the primary metric, minimum effect worth acting on, sample size, duration, segments, stopping rule, and analysis before viewing results. Use complete business cycles where relevant.
5. **Check assignment and instrumentation.** Verify randomization, exposure logging, event definitions, filters, consent, and tracking changes.
6. **Investigate sample-ratio mismatch (SRM).** Compare observed and expected assignment counts using the platform's SRM check or an appropriate statistical test under a prespecified criterion. A percentage difference alone is not proof of a defect; random variation depends on sample size. A statistical alert signals a possible quality issue but does not identify its cause. Investigate assignment, collection, filters, and segments before interpreting the treatment effect. Do not apply a universal threshold without justification.
7. **Read the effect, not only a p-value.** Consider effect size, interval, cost, guardrails, and practical value. A result informs this tested context; it does not validate a formula universally.
8. **Record learning.** Preserve the hypothesis, result, limitations, and next decision, including negative or inconclusive outcomes.

## Low traffic or weak instrumentation

A conventional A/B test may not detect small effects when conversions are scarce. Consider a larger strategic change, usability observation, interviews, support conversations, or review analysis. Treat qualitative evidence as a way to discover questions, not estimate prevalence. Before/after comparisons are vulnerable to seasonality, channel mix, and other concurrent changes.

Do not call a test inconclusive proof that versions are equal. Do not keep checking significance and stop at the first favorable result. Avoid changing several variables at once when the goal is to learn which change mattered.

## Funnel diagnosis

Behavioral signals are hypotheses, not diagnoses:

| Signal | Possible explanations to investigate | First check |
|---|---|---|
| Low ad click-through | Weak relevance, unclear message, audience mismatch, placement or creative issue | Segment, delivery, creative, and promise consistency |
| Clicks but few landing-page visits | Slow load, broken link, redirect, tracking or browser issue | Page speed and technical path |
| Visits but few product views | Navigation, availability, unclear offer, page experience | Usability and product findability |
| Product views but few add-to-carts | Fit, price, missing information, trust, stock | Product details, terms, reviews, inventory |
| Cart abandonment | Shipping, tax, fees, account requirement, error, payment issue, hesitation | Checkout telemetry and usability before persuasive copy |
| Checkout start but payment failure | Payment integration, declines, fraud controls, validation or outage | Technical error codes and provider status first |
| Leads but poor qualification | Targeting, offer, expectations, form fields, follow-up | Lead criteria and downstream quality |

Do not assume that abandonment means the user needs more trust copy. A technical error should first route to a technical investigation.

## Prioritization

There is no universal order of levers. Prioritize observed bottlenecks by evidence strength, decision impact, and effort. Changes to price, offer terms, availability, or guarantees are business decisions; present them as proposals and do not assume authority to make them.

## Source notes

See sources.md for references on SRM, experiment integrity, sample-size planning, checkout research, and web reading. Research estimates vary by setting. Use them as prompts for local investigation, not universal percentages or causal claims.
