# 5-minute assessment demo checklist

1. **Problem and goal (30 sec):** explain that this prototype reduces manual B2B lead research and helps a sales team prioritize companies for human review.
2. **Input (30 sec):** enter 3–5 companies and show the configurable ICP.
3. **Research (60 sec):** run live search; explain that public search results produce cited snippets and links.
4. **Scoring (60 sec):** open a lead and walk through the 100-point factor breakdown in the rationale.
5. **Uncertainty (45 sec):** show missing-information flags and a low-confidence or needs-research record. Explain that missing evidence does not equal a negative company signal.
6. **Exports (30 sec):** download CSV and JSON.
7. **Testing and guardrails (45 sec):** show `pytest -q`, the 25-company limit, no-outreach behavior, and human review requirement.

Assessment talking points:
- Search evidence is not treated as ground truth; citations make review possible.
- Scores are rule-based and reproducible, rather than an unexplained black-box number.
- A future iteration could add a licensed search API, page extraction with robots/terms compliance, a validated LLM extraction step with JSON schema, a persistent database, authentication, and calibration against reviewed historical leads.
