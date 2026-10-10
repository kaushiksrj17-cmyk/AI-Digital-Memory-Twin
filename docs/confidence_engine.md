# Confidence Engine Architecture & Scoring Methodology

## Overview
The **Confidence Engine** (`backend/app/services/confidence_engine.py`) calculates grounded reliability ratings for every conversational response in ECHO. Unlike black-box heuristics or ungrounded percentages, ECHO implements a deterministic, multi-factor evidentiary methodology rooted in claim-level corroboration, provenance pedigrees, and contradiction penalties.

---

## Tri-State Categorical Ratings

ECHO uses a user-friendly tri-state confidence model:

```
[ GREEN ]  VERIFIED
           All factual claims strictly substantiated by directly observed primary evidence.

[ YELLOW ] SUPPORTED INFERENCE
           Conclusions derived from multiple corroborating secondary items or contextual deduction.

[  RED  ]  UNKNOWN / UNSUPPORTED
           Evidence is absent, contradictory, or below threshold. Output states missing information.
```

---

## Mathematical Scoring Formula

For research and analytical transparency, a normalized confidence score $S_{\text{conf}} \in [0.0, 1.0]$ is computed as follows:

$$S_{\text{base}} = \frac{1.0 \cdot N_{\text{supported}} + 0.6 \cdot N_{\text{partial}}}{N_{\text{total}}}$$

### Deductions & Penalties:
1. **Contradiction Penalty**: If unacknowledged archival discrepancies exist:
   $$S = \max(0.4, S_{\text{base}} - 0.20)$$
2. **Unsupported Claim Penalty**: If unsupported assertions remain in candidate draft:
   $$S = \max(0.1, S - 0.30 \cdot N_{\text{unsupported}})$$
3. **Guardian Block Override**: If blocked by Memory Guardian:
   $$S = 0.0, \quad \text{Rating} = \text{UNKNOWN\_UNSUPPORTED}$$
4. **Zero-Evidence Case**: If no archival items match query:
   $$S = 0.0, \quad \text{Rating} = \text{UNKNOWN\_UNSUPPORTED}$$

### Rating Mapping:
- $S \ge 0.75 \implies \mathbf{VERIFIED}$
- $0.40 \le S < 0.75 \implies \mathbf{SUPPORTED\_INFERENCE}$
- $S < 0.40 \implies \mathbf{UNKNOWN\_UNSUPPORTED}$

---

## Explainable Methodology String
Every computed confidence value includes a self-documenting breakdown string:
```
"Confidence Methodology: Evaluated 3 claims: 2 fully supported, 1 partial, 0 unsupported, 0 conflicting."
```
This explanation is stored with the message record and presented to researchers in the inspection drawer.
