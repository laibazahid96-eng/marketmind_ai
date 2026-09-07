# Technical notes

## Safety

1. The API key is entered in the Streamlit sidebar and kept in session state.
2. `.env` and `runs/` are ignored by Git.
3. Retrieved text is treated as data, not as instructions.
4. Tool arguments are schema validated.
5. `save_research` rejects unresolved source references.
6. The agent loop has hard iteration and tool-call limits.
7. Approval is explicit; there is no default-yes path.

## Evidence discipline

Claims are typed as fact, inference, recommendation, or uncertainty. Unknown cells are represented as "not established" rather than guessed.

## QC

Mechanical checks are performed in Python for coverage and source references. The UI exposes the defect list before approval.

## Limitation

The included information tool is intentionally a deterministic fixture corpus rather than a live search API. For a production version, replace it with an approved search/retrieval provider and preserve the same provenance contract.
