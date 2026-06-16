# Agentic Pipelines for Digital Humanities

Three beginner-friendly notebooks for teaching the OpenAI Agents SDK to master's students in digital humanities.

The notebooks are fully runnable with the OpenAI Agents SDK, and include short setup notes where needed for local use and Google Colab.

## What the notebooks cover

1. `notebooks/01_single_agent_foundations.ipynb`
   - What an agent is
   - Messages, instructions, and task scope
   - Tools for simple DH workflows
   - Structured output and reproducibility

2. `notebooks/02_multi_agent_handoffs.ipynb`
   - Agents as tools
   - Specialized roles
   - Handoffs between agents
   - Coordinating a small pipeline

3. `notebooks/03_guardrails_and_human_in_the_loop.ipynb`
   - Guardrails and validation
   - Confidence and uncertainty
   - Human review checkpoints
   - Final export for archival or classroom use

## Suggested extra concepts

- State and context management
- Structured outputs vs free text
- Prompting for evidence and citations
- Error handling and fallback paths
- Evaluation and quality control
- Tracing and debugging runs
- Retrieval over local documents

## Setup with uv

```bash
uv sync
uv run jupyter lab
```

If you want to isolate notebook kernels, you can also register the environment:

```bash
uv run python -m ipykernel install --user --name agentic-example
```

## Google Colab

Use Colab if you want students to start without local setup.

1. Create a new notebook in Google Colab.
2. Run:

```python
!git clone https://github.com/<your-user>/agentic_example.git
%cd agentic_example
!pip install openai-agents pandas jupyterlab ipykernel
```

3. Set your API key:

```python
import os
os.environ["OPENAI_API_KEY"] = "YOUR_KEY"
```

4. Open the notebook files in the `notebooks/` folder and run cells top to bottom.

If you prefer not to clone a repo in class, copy the code cells into a single Colab notebook and install the same packages with `pip`.
