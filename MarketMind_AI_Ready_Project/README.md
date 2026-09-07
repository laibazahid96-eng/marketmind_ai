# MarketMind AI

https://marketmindai-eyycr4moarpnffyjwhy62p.streamlit.app/

A clean Streamlit implementation of the MarketMind AI capstone: a bounded business-research agent with manual tool dispatch, evidence provenance, structured Pydantic validation, QC, cost tracking, and an explicit human approval gate.

## Run locally

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

Open the app and paste your OpenAI API key in the **sidebar**. The key is kept in Streamlit session state only and is never written to `.env`, logs, or the repository.

## Important

This assignment explicitly forbids prebuilt agent executors and multi-agent orchestration frameworks. The agent loop, state, registry, and dispatcher in this project are implemented manually.

The information tool uses a small deterministic local corpus so evidence is reproducible. It does not secretly ask the LLM to invent sources.

## Main flow

Request → Scope analysis → Research plan → Bounded tool-calling loop → Evidence store → Comparison → Synthesis → QC → Human approval → Final report.

## Files

- `app.py` — Streamlit entry point
- `src/llm/client.py` — OpenAI Responses API wrapper with retries and usage
- `src/agents/pipeline.py` — bounded agent workflow
- `src/tools/dispatcher.py` — validation/permission/budget/dispatch layer
- `src/schemas/models.py` — structured schemas
- `src/state/research_state.py` — serializable run state
- `src/ui.py` — polished Streamlit interface
- `data/corpus.json` — reproducible fixture corpus
- `tests/test_core.py` — deterministic tests

## Deployment

For Streamlit Community Cloud, keep the repository secret-free. The app intentionally asks for the API key in the sidebar so you can run it without committing credentials.
