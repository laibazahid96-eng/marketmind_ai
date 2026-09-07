# Architecture

```text
Streamlit UI
   |
   v
Request Analyser -> Research Planner
   |                    |
   +--------------------+
             |
             v
      Manual Agent Loop
             |
        Tool Dispatcher
     /      |       |      \
 search  retrieve calculate compare
             |
             v
       Evidence Store
             |
             v
        Synthesis
             |
             v
      Deterministic QC
             |
             v
     Schema Report Draft
             |
             v
     HUMAN APPROVAL GATE
       /    |      |    \
 approve reject research rescope
```

The loop is bounded by iteration count and tool-call count. Tool arguments are JSON-schema validated before execution. Evidence records require a resolvable prior tool result.

The information source is a deterministic local fixture corpus, which is explicitly allowed by the assignment and makes the evaluation reproducible.
