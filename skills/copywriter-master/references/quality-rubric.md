# Editorial Quality Rubric

Rubric version: 1.1.0. This scoring contract is versioned separately from the skill release.

Score the final deliverable, not the effort spent. Use 0 = absent/incorrect, 1 = partial, 2 = fully meets the anchor. A total is a review aid, not conversion evidence. During external evaluation, a human reviewer assigns scores with a short rationale; do not treat a model's self-rating as independent validation.

| Dimension | 0 | 1 | 2 |
|---|---|---|---|
| Audience fit | Wrong audience or unsupported stereotypes | Broad but compatible | Uses the supplied audience and decision context |
| Offer clarity | Wrong offer or changed terms | Offer recognizable but unclear | Offer and material terms accurate and understandable |
| Evidence support | Invented, distorted, or unsupported fact | Claims traceable but scope/limits unclear | All factual claims supported and scoped; gaps held |
| CTA quality | Wrong, misleading, or missing requested action | Action present but vague | Clear next step matching the brief and destination |
| Compliance risk | Unconfirmed regulated benefit, hidden terms, fake scarcity, or privacy violation | Required review unresolved and not ready | Uses permitted scoped claims or omits held claims and clearly identifies review needs outside copy |
| Channel fit | Violates requested format, quantity, language, or limit | Usable with minor formatting work | Complete deliverable respecting all explicit constraints |
| Readability | Confusing, jargon-heavy, or contradictory | Understandable with avoidable friction | Concrete, concise, natural language and clear hierarchy |
| Emotional relevance | Manipulative fear or invented audience beliefs | Generic relevance | Recognizable supplied problem/desire without exaggeration |

For diagnosis/research-only outputs, Offer clarity means accurately representing the offer or identifying it as an unresolved gap; CTA quality means an actionable next decision rather than a sales CTA; Channel fit means the requested analytical structure. If the source has no audience language or offer, a precise gap is preferable to invention. Mark unknown context explicitly; do not award relevance for invented insight. For narrow tasks such as a single CTA, assess offer, evidence, and audience against the brief and what the line implies; do not add unused facts merely to fill dimensions.

## Hard failures

Record each independently, even when the total is high:

- `unsupported_claim`: invented or unsupported factual promise, comparison, testimonial, or outcome.
- `regulated_claim`: regulated benefit used without confirmed applicable permission, including softened wording.
- `false_scarcity`: invented or overstated deadline, stock, or availability.
- `changed_terms`: altered price, guarantee, cancellation condition, exact number, or other supplied term.
- `privacy_violation`: unnecessary identifiable customer data exposed in a shared deliverable.
- `scope_violation`: explicit quantity, length, language, requested mode, or format not followed.

A draft passes the editorial gate at **13/16 or more, no zero, and no hard failure**. Revise a low score. If evidence or permission is unavailable, remove/hold the claim and identify the gap where the requested format permits. A safe limited draft is possible; a pending regulated claim is never publishable because the total is high. Do not include a held claim in a copy-only response or disguise it with a placeholder.
