# URANO AuditoriaPR

Local-first pipeline for review analysis with explicit epistemic boundaries.

- Raw observations preserve original text, source and full SHA-256.
- Extracted aspects and sentiment are derived records linked to source observations.
- Aspect aggregation preserves positive and negative distributions instead of a single global score.
- Product hypotheses are conditional validation tasks, not claims of churn, revenue, scientific novelty or IP.
- The gate evaluates only derived hypotheses and never changes raw evidence.

The included extractor is a transparent deterministic baseline. It is not a calibrated ABSA model and must be validated against a labelled Portuguese corpus before operational promotion.

Run the unit tests with:

```bash
python -m unittest discover -s urano/auditoria_pr/tests -v
```
