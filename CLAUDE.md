# CLAUDE.md — Agentic Pipelines for Digital Humanities

This file documents the project for AI collaborators (Claude Code and others). Read it before suggesting changes or generating new content.

---

## Project purpose

This is a **teaching repository** for the [OpenAI Agents SDK](https://github.com/openai/openai-agents-python). It introduces agentic pipeline design through a Digital Humanities (DH) use case: extracting structured metadata from historical letters and archival texts.

Target audience: beginners to agent programming, typically researchers, students, or educators with some Python background but no prior agent SDK experience.

The four notebooks form a **deliberate learning progression**: each one adds exactly one new concept layer on top of the previous. Simplicity and clarity are primary values; exhaustiveness is not.

---

## Repository layout

```
.
├── data/                          # Six sample historical documents (txt)
│   ├── letter_01_madrid_1871.txt  # Clean letter — straightforward extraction
│   ├── letter_02_seville_1894.txt # Clean letter — publishing domain
│   ├── letter_03_ocr_fragment.txt # Noisy OCR fragment — triggers guardrails
│   ├── letter_04_barcelona_1902.txt # Clean letter — library/institution domain
│   ├── letter_05_porto_1888.txt   # Clean letter — cross-country correspondence
│   └── letter_06_ocr_table.txt    # Noisy subscriber table — non-letter format
├── notebooks/
│   ├── 01_single_agent_foundations.ipynb          # Single agent + tool + structured output
│   ├── 02_multi_agent_handoffs.ipynb              # Multi-agent: tools vs. handoffs
│   ├── 03_guardrails_and_human_in_the_loop.ipynb  # Input + output guardrails, HITL widget
│   ├── 04_end_to_end_pipeline.ipynb               # Full pipeline combining notebooks 1–3
│   ├── 05_evaluation.ipynb                        # Precision/recall/F1 harness
│   ├── 06_retrieval_and_tools.ipynb               # RAG + Wikipedia + Nominatim tools
│   └── 07_state_management.ipynb                  # ExtractionRegister, cross-doc queries
├── .github/workflows/notebooks.yml  # Manual CI workflow (workflow_dispatch)
├── .env.example                   # Template: copy to .env and add OPENAI_API_KEY
├── pyproject.toml                 # uv-managed deps; dev group: pytest, nbmake, pytest-asyncio
├── README.md                      # Setup instructions + concept overview
└── data.zip                       # Bundled data for Colab use
```

---

## Architecture and conventions

### Model

All notebooks share a single constant defined at the top of each notebook:

```python
DEFAULT_MODEL = "gpt-5.4-mini"
```

**Always use this constant** when creating agents. Never hardcode a model string elsewhere in a notebook. If the default model needs to change, update only this one line per notebook.

### Agent SDK patterns used

| Pattern | Introduced in | How it works |
|---|---|---|
| Single agent + tool | Notebook 1 | `Agent(name, instructions, tools=[fn_tool], output_type=Dataclass)` |
| Structured output | Notebook 1 | `@dataclass` with `default_factory=list` fields; passed as `output_type` |
| Agent-as-tool | Notebook 2 | `agent.as_tool(tool_name, description)` — string I/O |
| Handoff | Notebook 2 | `handoff(target_agent, tool_name_override='transfer_to_X')` |
| Input guardrail | Notebook 3 | `InputGuardrail(fn, name='')` + `GuardrailFunctionOutput(tripwire_triggered=bool)` |
| Guardrail exception | Notebooks 3–4 | `except InputGuardrailTripwireTriggered` wraps `Runner.run()` |
| Tracing | All | `with trace('label'):` around Runner.run() calls |

### Async convention

Notebooks run in Jupyter, so all agent calls use `await Runner.run()`, not `run_sync()`.

### Guardrail design philosophy

Guardrails in this repo are **deterministic and policy-based** (plain Python logic, no model calls). The confidence scoring in notebook 3 works by:
- Starting at `1.0`
- Subtracting `0.2` per uncertainty keyword ("unclear", "uncertain", "blurred", etc.)
- Subtracting `0.1` per OCR artifact pattern (`�`, digit-letter adjacency, etc.)
- Clamping to `[0.0, 1.0]`
- Triggering the guardrail when `uncertain=True OR confidence < 0.8`

This is intentionally simple so students understand the mechanism without a second model call.

### Code duplication across notebooks (intentional)

Notebook 4 copies definitions from notebooks 2 and 3 rather than importing them. **This is by design**: each notebook should be self-contained and runnable independently. Do not refactor shared code into a utility module unless adding a dedicated `05_shared_utilities.ipynb` that explicitly teaches that pattern.

### Extraction philosophy

Agents are instructed to be **conservative**: extract only what is explicitly stated in the text, include evidence quotations, and mark anything uncertain. This models good scholarly practice and is a recurring theme across all notebooks.

---

## Environment setup

```bash
# Local
cp .env.example .env         # then add your OPENAI_API_KEY
uv sync
uv run jupyter lab

# Colab (see README for full snippet)
!pip install openai-agents pandas jupyterlab ipykernel
import os; os.environ["OPENAI_API_KEY"] = "YOUR_KEY"
```

The `.env` file is gitignored. Never commit API keys.

---

## What is intentionally out of scope (for now)

The following topics are not yet covered and are candidates for future notebooks:

- Tracing and debugging deep-dives (a dedicated notebook beyond the dashboard tips)
- Embedding-based retrieval (notebook 06 covers keyword search; semantic search is the next step)
- Wikidata SPARQL enrichment (mentioned in notebook 06 discussion as an advanced topic)
- Persistent storage and database-backed state (notebook 07 covers in-memory; SQLite is the next step)

If you add a notebook covering one of these, name it `05_<topic>.ipynb` and follow the same pedagogical structure: concept explanation → minimal code → working example → exercise prompt.

---

## Data

The three `data/` files are designed as a minimal but illustrative set:

| File | Purpose |
|---|---|
| `letter_01_madrid_1871.txt` | Clean letter; straightforward extraction |
| `letter_02_seville_1894.txt` | Clean letter; different domain (publishing) |
| `letter_03_ocr_fragment.txt` | Deliberately noisy (OCR artifacts, ambiguous text); triggers guardrails |

`data.zip` bundles all three for Colab workflows. Keep both in sync when adding new data files.

If you add new data, use realistic historical text and include at least one noisy/ambiguous example to demonstrate guardrail behavior.

---

## Notebook structure template

Each notebook follows this structure:

1. **Objective cell** (markdown): one-paragraph statement of what this notebook teaches
2. **Setup cell**: imports, dotenv, `DEFAULT_MODEL`, tracing config
3. **Concept explanation** (markdown + minimal code blocks): introduce the idea before showing it
4. **Working example**: complete runnable demo using the data files
5. **Output inspection**: show how to read `result.final_output`, convert to DataFrame, etc.
6. **Exercise prompt** (markdown): open-ended extension for the student

Keep cells short. Prefer multiple focused cells over one long cell.

---

## Key enhancement opportunities (diagnostic)

The following gaps have been identified and are candidates for future work:

### High priority
- **No output guardrails**: Notebook 3 only shows input guardrails. Output guardrails (validating what the agent produces) are a natural next step and a gap in the teaching narrative.
- **Simulated human review**: The `human_review()` function in notebooks 3–4 prints a message but does not pause for real input. A real interactive checkpoint (e.g., `input()` prompt or a Jupyter widget) would make the HITL concept tangible.
- **No retry or error handling**: Agent calls have no retry logic for transient API errors. A brief example of wrapping `Runner.run()` with exponential backoff would improve robustness.

### Medium priority
- **Evaluation harness**: No notebook demonstrates how to measure extraction quality (precision/recall against a gold standard). This is critical for production DH work.
- **RAG over documents**: The README lists retrieval as a suggested concept but no notebook covers it. A notebook showing how to build a simple file-based retrieval tool would extend the single-agent pattern naturally.
- **More data variety**: The three sample letters are short and cover a narrow domain. Adding 2–3 more examples (different languages, different time periods, different document types) would make the demos more robust.
- **Notebook 5 (state management)**: A notebook showing how to pass context across multiple agent runs (e.g., maintaining a running extraction register) would close the curriculum gap on state.

### Low priority
- **pyproject.toml dev dependencies**: The `[dependency-groups] dev = []` section is empty. Adding `pytest` and `nbval` (for notebook testing) would enable CI validation.
- **No CI**: No GitHub Actions workflow exists. A simple workflow that runs `jupyter nbconvert --execute` on each notebook would catch broken imports or API changes early.
- **README doesn't mention the DH domain upfront**: The first paragraph could name the use case (historical letter analysis) to set expectations immediately.

---

## Collaboration guidelines for AI assistants

- **Preserve the pedagogical tone**: explanations before code, one concept per notebook, clear exercise prompts at the end.
- **Keep each notebook self-contained**: do not import from other notebooks or from a shared `utils.py`.
- **Match the existing instruction style**: agents receive precise, conservative instructions with explicit uncertainty handling. Do not make instructions vague.
- **Use `DEFAULT_MODEL`**: never hardcode a model string in agent definitions.
- **Respect the data domain**: changes to data files or agent instructions should remain consistent with the DH framing (historical documents, archival extraction, scholarly conservatism).
- **Do not add dependencies** without updating `pyproject.toml` and verifying `uv sync` succeeds.
- **Test notebooks top-to-bottom**: after any change, verify that all cells execute without error in a fresh kernel. The cells must be runnable in order.
