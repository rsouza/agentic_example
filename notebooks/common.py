from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


NOTEBOOK_DIR = Path(__file__).resolve().parent
DATA_DIR = NOTEBOOK_DIR.parent / "data"


def _read_text(filename: str) -> str:
    return (DATA_DIR / filename).read_text(encoding="utf-8").strip()


LETTER_TEXTS = [
    {
        "id": 1,
        "title": "Letter from Madrid, 1871",
        "text": _read_text("letter_01_madrid_1871.txt"),
    },
    {
        "id": 2,
        "title": "Printing House Notice, 1894",
        "text": _read_text("letter_02_seville_1894.txt"),
    },
    {
        "id": 3,
        "title": "OCR Fragment",
        "text": _read_text("letter_03_ocr_fragment.txt"),
    },
]

NEWSPAPER_SNIPPETS = [
    "Madrid, 12 May 1894. The exhibition opened yesterday to a crowded hall.",
    "Seville, 3 June 1894. The printing house announced a second edition of poems.",
]


@dataclass
class ReviewDecision:
    record_id: int
    uncertain: bool
    confidence: float
    notes: str
