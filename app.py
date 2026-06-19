from __future__ import annotations

import os
from dataclasses import asdict
from pathlib import Path

import gradio as gr

from src.hf_runner import HFPipeline


_PIPELINE: HFPipeline | None = None


def _discover_documents(data_dir: str) -> list[str]:
    base = Path(data_dir)
    if not base.exists():
        return []
    return [p.name for p in sorted(base.glob("*.txt"))]


def _get_pipeline() -> HFPipeline:
    global _PIPELINE
    if _PIPELINE is None:
        _PIPELINE = HFPipeline(
            data_dir=os.getenv("DATA_DIR", "data"),
            model_id=os.getenv("HF_MODEL_ID", "Qwen/Qwen2.5-1.5B-Instruct"),
            device_map=os.getenv("HF_DEVICE_MAP", "auto"),
        )
    return _PIPELINE


def run_pipeline(filename: str, approve_uncertain: bool):
    if not filename:
        return "No file selected.", {}, {}, {}

    pipeline = _get_pipeline()
    text = pipeline.documents[filename]
    decision = pipeline.review_decision_from_text(text)
    action = "approved"
    if decision.uncertain:
        action = "approved" if approve_uncertain else "archived"

    result = pipeline.run_document(filename, human_action=action)
    status = (
        f"File: {result.filename}\n"
        f"Guardrail uncertain: {result.decision.uncertain}\n"
        f"Confidence: {result.decision.confidence}\n"
        f"Notes: {result.decision.notes}\n"
        f"Human action: {result.action}"
    )

    extraction = asdict(result.extraction) if result.extraction else {}
    return status, extraction, result.wikipedia, result.geocodes


DOC_CHOICES = _discover_documents(os.getenv("DATA_DIR", "data"))


with gr.Blocks(title="DH Agentic Pipeline (Local HF)") as demo:
    gr.Markdown("# DH Agentic Pipeline (Local HF)")
    gr.Markdown(
        "Runs notebook-style review -> human gate -> extraction -> enrichment "
        "using a local Hugging Face model."
    )

    with gr.Row():
        filename = gr.Dropdown(choices=DOC_CHOICES, label="Document", value=DOC_CHOICES[0] if DOC_CHOICES else None)
        approve_uncertain = gr.Checkbox(
            value=False,
            label="If uncertain, approve instead of archive",
        )

    run_btn = gr.Button("Run pipeline", variant="primary")

    status = gr.Textbox(label="Run status", lines=7)
    extraction = gr.JSON(label="Extraction")
    wikipedia = gr.JSON(label="Wikipedia summaries by place")
    geocodes = gr.JSON(label="Geocodes by place")

    run_btn.click(
        fn=run_pipeline,
        inputs=[filename, approve_uncertain],
        outputs=[status, extraction, wikipedia, geocodes],
    )


if __name__ == "__main__":
    demo.launch()
