# ECHO Hybrid Retrieval Architecture & Scoring Model

## 1. Multi-Strategy Synthesis

The **ECHO Retrieval Engine** supports four distinct retrieval strategies:
1. `VECTOR`: Dense nearest-neighbor similarity over semantic embeddings.
2. `KEYWORD`: Exact token and phrase frequency matching.
3. `GRAPH`: Entity neighborhood and relational edge traversal.
4. `HYBRID`: Weighted linear combination synthesizing vector, keyword, and graph signals.

---

## 2. Explainable Composite Scoring

In `HYBRID` mode, final candidate ranking is governed by an explainable scoring function:

$$\text{Score} = w_{\text{vec}} \cdot S_{\text{vector}} + w_{\text{kw}} \cdot S_{\text{keyword}} + w_{\text{graph}} \cdot S_{\text{graph}} + \text{Bonus}_{\text{verified}}$$

Default weights:
- $w_{\text{vec}} = 0.50$ (semantic proximity)
- $w_{\text{kw}} = 0.30$ (exact token matching)
- $w_{\text{graph}} = 0.20$ (relational connection)
- $\text{Bonus}_{\text{verified}} = +0.05$ (reward for primary authenticated documents)

Every result returned to the user exposes:
- `score`: Composite confidence score $[0.0, 1.0]$
- `score_components`: Explicit breakdown across vector, keyword, graph, and confidence bonus
- `why_retrieved`: Human-readable explanation (e.g., `"Semantic similarity + Exact token match (Cambridge, 1968) (Verified primary source)"`)

---

## 3. Privacy & Boundary Gating

Retrieval filters are applied **before** returning candidates:
- `PRIVATE`: Accessible only to the vault owner / primary guardian.
- `FAMILY`: Accessible to authorized family circle members.
- `AUTHORIZED_USERS`: Accessible to accredited researchers and invited users.
- Revoked consent items are omitted from AI-derived searches.
