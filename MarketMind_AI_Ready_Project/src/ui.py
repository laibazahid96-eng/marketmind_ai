import json, os, time
import streamlit as st
from .config import settings
from .llm.client import LLMClient, LLMError
from .agents.pipeline import Pipeline
from .state.research_state import ResearchState

CSS = """
<style>
.block-container {padding-top: 1.5rem; max-width: 1400px;}
.hero {padding: 1.3rem 1.5rem; border-radius: 18px; background: linear-gradient(135deg,#111827,#243b53); color:white; margin-bottom:1rem;}
.hero h1 {font-size: 2.3rem; margin:0;}
.hero p {color:#cbd5e1; margin:.35rem 0 0;}
.card {padding:1rem; border:1px solid rgba(128,128,128,.25); border-radius:14px; background:rgba(128,128,128,.05);}
.small {font-size:.86rem; opacity:.75;}
</style>
"""

def render_app():
    st.markdown(CSS, unsafe_allow_html=True)
    if "api_key" not in st.session_state:
        st.session_state.api_key = ""
    if "report" not in st.session_state:
        st.session_state.report = None
    if "state" not in st.session_state:
        st.session_state.state = None
    if "pipeline" not in st.session_state:
        st.session_state.pipeline = None

    with st.sidebar:
        st.markdown("## 🔐 API Access")
        key = st.text_input("OpenAI API key", type="password", value=st.session_state.api_key,
                            placeholder="sk-...", help="Used only for this session. Never saved to disk.")
        st.session_state.api_key = key.strip()
        st.divider()
        st.markdown("### ⚙️ Run limits")
        st.caption(f"Model: `{settings.model}`")
        st.caption(f"Max iterations: {settings.max_iterations}")
        st.caption(f"Max tool calls: {settings.max_tool_calls}")
        st.caption(f"Budget ceiling: ${settings.max_budget_usd:.2f}")
        st.divider()
        st.info("Tip: start with the reference scenario: “Research the market for AI-powered customer support software and prepare a business intelligence report.”")

    st.markdown('<div class="hero"><h1>📊 MarketMind AI</h1><p>Autonomous business research • evidence-first • bounded agent loop • human approval</p></div>', unsafe_allow_html=True)

    if not st.session_state.api_key:
        st.warning("Enter your OpenAI API key in the sidebar to unlock research.")
        st.text_area("Research request", value="Research the market for AI-powered customer support software and prepare a business intelligence report.", disabled=True)
        return

    col1, col2 = st.columns([3,1])
    with col1:
        request = st.text_area("Business research request", height=130,
                                placeholder="Example: Research the market for AI coding assistants and identify competitive gaps.")
    with col2:
        st.markdown("### Status")
        st.success("API key ready")
        if st.session_state.state:
            st.caption(f"Run: `{st.session_state.state.run_id}`")

    run = st.button("🚀 Start Market Research", type="primary", use_container_width=True)
    if run:
        if len(request.strip()) < 10:
            st.error("Please enter a meaningful research request.")
            return
        try:
            llm = LLMClient(st.session_state.api_key, settings.model, settings.request_timeout)
            pipe = Pipeline(llm, settings)
            state = ResearchState(request=request.strip())
            with st.status("Running MarketMind pipeline…", expanded=True) as status:
                st.write("🔎 Analysing request and ambiguity…")
                scope = pipe.analyze(request, state)
                st.write("🧭 Building validated research plan…")
                pipe.plan(scope, request, state)
                st.write("🛠️ Running bounded research/tool loop…")
                pipe.research_loop(request, state)
                st.write("🧪 Running deterministic quality checks…")
                pipe.qc(state)
                st.write("🧠 Synthesising evidence…")
                synthesis = pipe.synthesis(request, state)
                st.write("📝 Building schema-validated report draft…")
                report = pipe.build_report(request, state, synthesis)
                state.save()
                st.session_state.state = state
                st.session_state.report = report.model_dump()
                st.session_state.pipeline = pipe
                status.update(label="Research draft ready for human approval", state="complete")
        except LLMError as e:
            st.error(str(e))
        except Exception as e:
            st.error(f"Unexpected error handled safely: {e}")

    if st.session_state.report and st.session_state.state:
        render_results()

def render_results():
    state = st.session_state.state
    report = st.session_state.report
    pipe = st.session_state.pipeline

    st.divider()
    st.subheader("Research Run")
    a,b,c,d = st.columns(4)
    a.metric("Evidence", len(state.evidence))
    b.metric("Tool calls", len(state.tool_history))
    c.metric("Iterations", state.iteration_count)
    d.metric("Est. cost", f"${pipe.usage.estimated_cost:.4f}" if pipe else "$0")

    tabs = st.tabs(["📌 Scope", "🧭 Plan", "🔗 Evidence", "🧪 QC", "📄 Report", "👤 Approval"])
    with tabs[0]:
        st.json(state.scope)
    with tabs[1]:
        st.json(state.plan)
    with tabs[2]:
        if state.evidence:
            for e in state.evidence:
                st.markdown(f"**{e['evidence_id']} · {e['claim_type'].upper()} · {e['confidence']}**")
                st.write(e["claim"])
                st.caption(f"Source ref: {e['source_ref']} · {e['source_detail']}")
                st.divider()
        else:
            st.info("No evidence was established.")
    with tabs[3]:
        if state.defects:
            st.warning(f"{len(state.defects)} QC issue(s) recorded.")
            for d in state.defects:
                st.write(f"**{d['severity'].upper()} — {d['type']}** · {d['location']}: {d['message']}")
        else:
            st.success("No deterministic QC defects found.")
    with tabs[4]:
        st.markdown("### Executive Summary")
        st.write(report["executive_summary"])
        st.markdown("### Market Overview")
        for f in report["market_overview"]:
            st.info(f"{f['claim_type'].upper()} · {f['confidence']}\n\n{f['statement']}")
        st.markdown("### Limitations & Gaps")
        for x in report["limitations_and_gaps"]:
            st.write("• " + x)
        with st.expander("Full schema-validated JSON"):
            st.json(report)
    with tabs[5]:
        st.warning("Nothing is published automatically. A human must explicitly choose an outcome.")
        st.write(f"**Confidence:** {report['confidence_level']} — {report['rationale']}")
        decision = st.selectbox("Decision", ["Select…","Approve","Reject","Request additional research","Modify scope"])
        notes = st.text_area("Reviewer notes")
        if st.button("Save decision", type="primary"):
            if decision == "Select…":
                st.error("Choose an explicit decision.")
            else:
                report["approval"] = {
                    "approver": "Streamlit reviewer",
                    "decision": decision,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "notes": notes
                }
                state.save()
                st.session_state.report = report
                if decision == "Approve":
                    os.makedirs(f"runs/{state.run_id}", exist_ok=True)
                    with open(f"runs/{state.run_id}/final_report.json","w",encoding="utf-8") as f:
                        json.dump(report,f,indent=2,ensure_ascii=False)
                    st.success("Approved. Final report saved to the run artefact folder.")
                elif decision == "Reject":
                    st.error("Rejected. Nothing was published.")
                else:
                    st.info(f"{decision} recorded. Re-run with the new scope/questions before publishing.")
