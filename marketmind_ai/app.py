import streamlit as st
import json
from src.llm import ReliableLLMClient
from src.tools import ToolDispatcher
from src.agents import AutonomousResearchLoop

st.set_page_config(
    page_title="MarketMind AI",
    page_icon="🤖",
    layout="wide"
)

# 1. Initialize session state for the API key if it doesn't exist
if "openai_api_key" not in st.session_state:
    st.session_state["openai_api_key"] = ""

# 2. Key Input / Gatekeeper Page
if not st.session_state["openai_api_key"]:
    st.title("Welcome to MarketMind AI")
    st.subheader("Please enter your OpenAI API Key to proceed")
    
    with st.form("api_key_form"):
        user_key = st.text_input(
            "OpenAI API Key",
            type="password",
            placeholder="sk-proj-...",
            help="Enter your OpenAI API Key starting with 'sk-'"
        )
        submitted = st.form_submit_button("Submit & Proceed")
        
        if submitted:
            if user_key.startswith("sk-") or len(user_key) > 20:
                st.session_state["openai_api_key"] = user_key
                st.success("API Key accepted! Loading application...")
                st.rerun()  # Refresh app to load the main page
            else:
                st.error("Please enter a valid OpenAI API key.")
    
    st.stop()  # Prevents rendering any subsequent UI elements until an API key is provided

# ---------------------------------------------------------
# 3. Main Dashboard Page (Only rendered after API key submission)
# ---------------------------------------------------------

st.title("MarketMind AI - Autonomous Research Loop")

# Sidebar Configuration
st.sidebar.header("Configuration")

# Option to update or clear key from the sidebar
if st.sidebar.button("Logout / Change API Key"):
    st.session_state["openai_api_key"] = ""
    st.rerun()

max_iterations = st.sidebar.number_input("Max Iterations", min_value=1, max_value=20, value=10)
cost_ceiling = st.sidebar.number_input("Cost Ceiling ($)", min_value=0.1, max_value=10.0, value=2.0, step=0.5)

# Cached agent initialization with session key
@st.cache_resource
def get_agent(api_key: str):
    llm = ReliableLLMClient(api_key=api_key)
    dispatcher = ToolDispatcher()
    return AutonomousResearchLoop(
        llm_client=llm, 
        dispatcher=dispatcher, 
        max_iterations=max_iterations, 
        cost_ceiling_usd=cost_ceiling
    )

agent = get_agent(st.session_state["openai_api_key"])

# Research Plan Execution UI
st.subheader("Execute Research Plan")
default_plan = {
    "scope_summary": "Competitor pricing analysis for SaaS platforms",
    "objectives": [
        {
            "id": "OBJ-1",
            "title": "Pricing Analysis",
            "description": "Determine current subscription tiers for target platforms."
        }
    ]
}

plan_input = st.text_area(
    "Research Plan JSON", 
    value=json.dumps(default_plan, indent=2), 
    height=200
)

if st.button("Run Agent Loop"):
    try:
        plan_data = json.loads(plan_input)
        with st.spinner("Executing autonomous research loop..."):
            results = agent.execute_plan(plan_data)
            
        st.success(f"Execution finished with status: {results['status']}")
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Status", results["status"])
        col2.metric("Total Cost", f"${results['accumulated_cost']:.4f}")
        col3.metric("Iterations Used", results["iterations"])
        
        st.subheader("Evidence Store")
        if results["evidence_store"]:
            st.json([ev.dict() for ev in results["evidence_store"]])
        else:
            st.write("No evidence records captured.")
            
        st.subheader("Tool Execution History")
        st.json(results["tool_history"])
        
    except json.JSONDecodeError:
        st.error("Invalid JSON format in the Research Plan input.")
    except Exception as e:
        st.error(f"An error occurred during execution: {str(e)}")