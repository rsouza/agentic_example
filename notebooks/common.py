from __future__ import annotations

from dataclasses import dataclass

LETTER_TEXTS = [
    {
        "id": 1,
        "title": "Letter from Madrid, 1871",
        "text": "In 1871, Maria Gomez wrote from Madrid to her brother in Valencia about the exhibition and the costs of travel.",
    },
    {
        "id": 2,
        "title": "Printing House Notice, 1894",
        "text": "The printer in Seville announced a new edition of poems by Antonio Ruiz and asked readers to send subscriptions.",
    },
    {
        "id": 3,
        "title": "OCR Fragment",
        "text": "Madrld, 1871. Ma^ria Go'mez wrofe to her brotner about the exhlbition.",
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
