from __future__ import annotations

import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path


UNCERTAINTY_KEYWORDS = (
    "unclear",
    "uncertain",
    "blurred",
    "illeg",
    "unread",
    "torn",
    "draft transcription",
)

OCR_PATTERNS = (
    re.compile(r"�"),
    re.compile(r"[A-Za-z]\d|\d[A-Za-z]"),
    re.compile(r"\[.*\?\]"),
)


@dataclass
class ReviewDecision:
    uncertain: bool
    confidence: float
    notes: str


@dataclass
class Extraction:
    people: list[str] = field(default_factory=list)
    places: list[str] = field(default_factory=list)
    dates: list[str] = field(default_factory=list)
    evidence: list[str] = field(default_factory=list)


@dataclass
class PipelineOutput:
    filename: str
    decision: ReviewDecision
    action: str
    extraction: Extraction | None = None
    wikipedia: dict[str, str] = field(default_factory=dict)
    geocodes: dict[str, str] = field(default_factory=dict)


class LocalPipeline:
    """Notebook-equivalent pipeline without SDK.

    Orchestration pattern: review -> human gate -> extract -> enrich.
    Model hook is intentionally simple and swappable for HF transformers.
    """

    def __init__(self, data_dir: str = "data", user_agent: str = "agentic-example/0.1"):
        self.data_dir = Path(data_dir)
        self.user_agent = user_agent
        self.documents = self._load_documents()

    def _load_documents(self) -> dict[str, str]:
        if not self.data_dir.exists():
            raise FileNotFoundError(f"data directory not found: {self.data_dir}")
        docs: dict[str, str] = {}
        for path in sorted(self.data_dir.glob("*.txt")):
            docs[path.name] = path.read_text(encoding="utf-8").strip()
        if not docs:
            raise FileNotFoundError(f"no .txt files found in: {self.data_dir}")
        return docs

    def review_decision_from_text(self, text: str) -> ReviewDecision:
        lowered = text.lower()
        notes: list[str] = []
        confidence = 1.0

        kw_hits = sum(1 for kw in UNCERTAINTY_KEYWORDS if kw in lowered)
        if kw_hits:
            confidence -= 0.2 * kw_hits
            notes.append("uncertainty language detected")

        pattern_hits = sum(1 for pat in OCR_PATTERNS if pat.search(text))
        if pattern_hits:
            confidence -= 0.1 * pattern_hits
            notes.append("ocr artifact signals detected")

        confidence = max(0.0, min(1.0, confidence))
        uncertain = kw_hits > 0 or confidence < 0.8
        return ReviewDecision(
            uncertain=uncertain,
            confidence=round(confidence, 2),
            notes="; ".join(notes) if notes else "clear enough to process",
        )

    def search_documents(self, query: str) -> str:
        hits: list[str] = []
        for filename, text in self.documents.items():
            for line in text.splitlines():
                if query.lower() in line.lower() and line.strip():
                    hits.append(f"[{filename}] {line.strip()}")
        if not hits:
            return f"No documents matched '{query}'."
        return "\n".join(hits)

    def wikipedia_summary(self, topic: str) -> str:
        encoded = urllib.parse.quote(topic.replace(" ", "_"))
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}"
        req = urllib.request.Request(url, headers={"User-Agent": self.user_agent})
        try:
            with urllib.request.urlopen(req, timeout=8) as response:
                data = json.loads(response.read())
            extract = data.get("extract", "")
            return extract if extract else f"No Wikipedia summary found for '{topic}'."
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                return f"No Wikipedia article found for '{topic}'."
            return f"Wikipedia lookup failed ({exc.code}): {exc.reason}"
        except Exception as exc:
            return f"Wikipedia lookup failed: {exc}"

    def geocode_place(self, place_name: str) -> str:
        time.sleep(1)
        params = urllib.parse.urlencode({"q": place_name, "format": "json", "limit": "1"})
        url = f"https://nominatim.openstreetmap.org/search?{params}"
        req = urllib.request.Request(url, headers={"User-Agent": self.user_agent})
        try:
            with urllib.request.urlopen(req, timeout=8) as response:
                results = json.loads(response.read())
            if not results:
                return f"No coordinates found for '{place_name}'."
            result = results[0]
            return (
                f"{place_name}: lat={result['lat']}, lon={result['lon']}\n"
                f"Resolved as: {result.get('display_name', 'unknown')}"
            )
        except Exception as exc:
            return f"Geocoding failed for '{place_name}': {exc}"

    def _extract_with_local_model(self, text: str) -> Extraction:
        """Placeholder extraction logic.

        Replace this method with a local HF model call, e.g. transformers pipeline.
        """
        people = sorted(set(re.findall(r"\b[A-Z][a-z]+\s+[A-Z][a-z]+\b", text)))
        places = sorted({p for p in ["Madrid", "Seville", "Barcelona", "Porto", "Valencia", "Lisbon", "Girona", "Braga"] if p in text})
        dates = sorted(set(re.findall(r"\b\d{1,2}\s+[A-Z][a-z]+\s+\d{4}\b|\b\d{4}\b", text)))
        evidence = [line.strip() for line in text.splitlines() if any(token in line for token in ("Madrid", "Seville", "Barcelona", "Porto", "187", "188", "189", "190"))][:5]
        return Extraction(people=people, places=places, dates=dates, evidence=evidence)

    def run_document(self, filename: str, human_action: str | None = None) -> PipelineOutput:
        if filename not in self.documents:
            raise KeyError(f"unknown filename: {filename}")

        text = self.documents[filename]
        decision = self.review_decision_from_text(text)

        action = "approved"
        if decision.uncertain:
            action = (human_action or "archived").strip().lower()
            if action not in {"approved", "archived"}:
                raise ValueError("human_action must be 'approved' or 'archived'")

        output = PipelineOutput(filename=filename, decision=decision, action=action)
        if action == "archived":
            return output

        extraction = self._extract_with_local_model(text)
        output.extraction = extraction

        for place in extraction.places:
            output.wikipedia[place] = self.wikipedia_summary(place)
            output.geocodes[place] = self.geocode_place(place)
        return output


def _demo() -> None:
    pipeline = LocalPipeline(data_dir="data")
    for name in sorted(pipeline.documents.keys()):
        human_action = "approved" if "ocr" not in name else "archived"
        result = pipeline.run_document(name, human_action=human_action)
        print(f"\n--- {name} ---")
        print(f"decision={result.decision} action={result.action}")
        if result.extraction:
            print("extraction:", result.extraction)
            print("places enriched:", list(result.wikipedia.keys()))


if __name__ == "__main__":
    _demo()
