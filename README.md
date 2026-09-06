
## 🚀 Quickstart Guide

### 1. Prerequisites
* Python 3.10+
* OpenAI API Key (`sk-...`)

### 2. Installation
Clone the repository and install the dependencies:
```bash
git clone https://github.com/your-org/marketmind.git
cd marketmind
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Environment Setup
Copy `.env.example` to `.env` and insert your OpenAI API Key:
```bash
cp .env.example .env
```
In `.env`:
```env
OPENAI_API_KEY=sk-proj-...
```

---

## 💻 Running the Application

### Option A: Interactive Streamlit Web UI
Launch the interactive dashboard to run agent loops, inspect tool calls, and review results:
```bash
streamlit run app.py
```
1. Access `http://localhost:8501` in your browser.
2. Enter your OpenAI API Key when prompted.
3. Define or edit the research plan JSON and click **Run Agent Loop**.

### Option B: Command Line Script
Run a quick research loop demonstration via script:
```bash
python run.py
```

### Option C: System Smoke Test
Verify that the full multi-agent pipeline, tool dispatcher, and LLM clients are working properly:
```bash
python smoke_test.py
```

---

## 📊 Evaluation & Benchmarking

To benchmark system performance across pre-defined test cases:
```bash
python evaluation/run_eval.py
```

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.