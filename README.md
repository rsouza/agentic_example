# Agentic Pipelines for Digital Humanities

Seven runnable notebooks for building agentic pipelines with the OpenAI Agents SDK.
The running example throughout is historical letter analysis: extracting people, places,
dates, and evidence from archival texts. Each notebook introduces one new concept layer
and is fully self-contained.

## What the notebooks cover

1. `notebooks/01_single_agent_foundations.ipynb`
   - What an agent is
   - Instructions, tools, and task scope
   - Structured output and reproducibility

2. `notebooks/02_multi_agent_handoffs.ipynb`
   - Agents as tools
   - Specialized roles
   - Handoffs between agents
   - Coordinating a small pipeline

3. `notebooks/03_guardrails_and_human_in_the_loop.ipynb`
   - Input and output guardrails
   - Confidence and uncertainty
   - Interactive human review checkpoints

4. `notebooks/04_end_to_end_pipeline.ipynb`
   - Single-agent extraction
   - Agents as tools and handoffs
   - Guardrails in one workflow

5. `notebooks/05_evaluation.ipynb`
   - Gold-standard annotations
   - Precision, recall, and F1
   - Scoring extractions across a document collection

6. `notebooks/06_retrieval_and_tools.ipynb`
   - Retrieval-Augmented Generation over local files
   - API tools with no authentication (Wikipedia, Nominatim)
   - Multi-tool agents and responsible API use

7. `notebooks/07_state_management.ipynb`
   - Accumulating results across multiple agent runs
   - Provenance tracking
   - Cross-document queries and co-occurrence analysis

## Setup with uv

```bash
uv sync
uv run jupyter lab
```

To isolate notebook kernels:

```bash
uv run python -m ipykernel install --user --name agentic-example
```

## Local API key

1. Copy `.env.example` to `.env`.
2. Add your `OPENAI_API_KEY` value to `.env`.
3. Reopen the notebook or restart the kernel.

The notebooks load `.env` automatically when run locally.

## Google Colab

1. Create a new notebook in Google Colab.
2. Run:

```python
!git clone https://github.com/<your-user>/agentic_example.git
%cd agentic_example
!pip install openai-agents pandas jupyterlab ipykernel ipywidgets
```

3. Set your API key using **Colab Secrets** (recommended):
   - Click the key icon in the left sidebar (or go to **Tools → Secrets**).
   - Add a secret named `OPENAI_API_KEY` with your key as the value.
   - Enable notebook access for that secret.
   - Load it in a code cell:

```python
from google.colab import userdata
import os
os.environ["OPENAI_API_KEY"] = userdata.get("OPENAI_API_KEY")
```

   Using Secrets keeps your key out of the notebook file and out of version control.
   Never paste a live API key directly into a cell — Colab autosaves notebooks and
   the key would be stored in plain text.

4. Open the notebook files in the `notebooks/` folder and run cells top to bottom.

Alternatively, copy the code cells into a single Colab notebook and install the same packages with `pip`.

## Hugging Face Spaces (local HF model)

This repo now includes a script-based (non-SDK) runtime in `src/` and a Gradio app in `app.py`.
It mirrors the notebook pipeline conceptually:

- Input review guardrail (`review_decision_from_text`)
- Human gate (`approved` vs `archived`)
- Extraction with a local Hugging Face model
- Optional enrichment with Wikipedia and Nominatim

### Files

- `app.py`: Gradio UI entrypoint for Spaces
- `src/pipeline.py`: SDK-free orchestration and tools
- `src/hf_runner.py`: local HF model integration
- `pyproject.hf.toml`: separate dependency definition for HF deployment
- `requirements-hf.txt`: explicit pip requirements for HF Spaces

### Environment variables (optional)

- `HF_MODEL_ID` (default: `Qwen/Qwen2.5-1.5B-Instruct`)
- `HF_DEVICE_MAP` (default: `auto`)
- `DATA_DIR` (default: `data`)

### Local run

Install the dependencies from `pyproject.hf.toml` (or equivalent `pip` install), then:

```bash
uv run python app.py
```

Or with pip-compatible requirements for the HF deployment path:

```bash
pip install -r requirements-hf.txt
python app.py
```

### Hugging Face Spaces setup

1. Create a new **Gradio** Space.
2. Push this repository contents to the Space.
3. Ensure `data/` is present in the Space repo (or set `DATA_DIR` to your mounted path).
4. Install dependencies from `pyproject.hf.toml` (or mirror them in `requirements.txt`).
5. Set `app.py` as the Space app entrypoint.

If you prefer pip-style installation in Spaces, use `requirements-hf.txt`.

Notes:
- The script runtime is intentionally explicit and deployment-oriented.
- The notebooks remain the pedagogical SDK path; `src/` is the production-style local-model path.
