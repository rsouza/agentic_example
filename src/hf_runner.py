from __future__ import annotations

import json

from transformers import pipeline

from src.pipeline import Extraction, LocalPipeline


class HFPipeline(LocalPipeline):
    """LocalPipeline variant with a local Hugging Face text-generation model."""

    def __init__(
        self,
        data_dir: str = "data",
        model_id: str = "Qwen/Qwen2.5-1.5B-Instruct",
        device_map: str = "auto",
    ):
        super().__init__(data_dir=data_dir)
        self.generator = pipeline(
            "text-generation",
            model=model_id,
            device_map=device_map,
        )

    def _extract_with_local_model(self, text: str) -> Extraction:
        prompt = (
            "Extract people, places, dates, and evidence from the text. "
            "Return strict JSON with keys: people, places, dates, evidence.\n\n"
            f"TEXT:\n{text[:5000]}"
        )
        result = self.generator(prompt, max_new_tokens=400, do_sample=False)[0]["generated_text"]
        json_start = result.find("{")
        json_end = result.rfind("}")
        if json_start == -1 or json_end == -1:
            return Extraction()
        try:
            payload = json.loads(result[json_start : json_end + 1])
        except json.JSONDecodeError:
            return Extraction()
        return Extraction(
            people=list(payload.get("people", [])),
            places=list(payload.get("places", [])),
            dates=list(payload.get("dates", [])),
            evidence=list(payload.get("evidence", [])),
        )


def main() -> None:
    pipeline = HFPipeline()
    result = pipeline.run_document("letter_01_madrid_1871.txt", human_action="approved")
    print(result)


if __name__ == "__main__":
    main()
