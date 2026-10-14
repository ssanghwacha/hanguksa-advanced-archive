from __future__ import annotations

import json
import re
from pathlib import Path

from pypdf import PdfReader, PdfWriter

ROOT = Path(__file__).resolve().parent
PDFS = ROOT / "source-pdfs"
OUTPUT = ROOT / "output" / "pdf" / "hanguksa-advanced-past-questions-62-79.pdf"
SITE_DATA = ROOT / "site" / "answers.json"
SITE_SCRIPT = ROOT / "site" / "answers.js"

ROUNDS = [62, 64, 66, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79]
DATES = {
    62: "2022.12.03", 64: "2023.04.15", 66: "2023.08.13", 68: "2023.12.02",
    69: "2024.02.17", 70: "2024.05.25", 71: "2024.08.10", 72: "2024.10.20",
    73: "2025.02.16", 74: "2025.05.24", 75: "2025.08.09", 76: "2025.10.18",
    77: "2026.02.07", 78: "2026.05.23", 79: "2026.08.09",
}

def extract_answers(round_no: int) -> list[str]:
    text = PdfReader(PDFS / f"answer-{round_no}.pdf").pages[0].extract_text()
    matches = re.findall(r"(?<!\d)([1-9]|[1-4]\d|50)\s+([①②③④⑤]|[1-5])\s+[123](?!\d)", text)
    numerals = {"1": "①", "2": "②", "3": "③", "4": "④", "5": "⑤"}
    answers = {int(number): numerals.get(choice, choice) for number, choice in matches}
    if sorted(answers) != list(range(1, 51)):
        raise ValueError(f"{round_no}회 정답표 추출 실패: {len(answers)}개")
    return [answers[number] for number in range(1, 51)]

def create_combined_pdf() -> None:
    writer = PdfWriter()
    for round_no in reversed(ROUNDS):
        writer.append(PdfReader(PDFS / f"{round_no}.pdf"))
    with OUTPUT.open("wb") as stream:
        writer.write(stream)

def create_site_data() -> None:
    payload = {"title": "한능검 심화 기출 정답", "rounds": []}
    for round_no in ROUNDS:
        payload["rounds"].append({
            "round": round_no,
            "date": DATES[round_no],
            "answers": extract_answers(round_no),
            "source": "https://www.historyexam.go.kr/pst/list.do?bbs=dat",
            "answerVerified": True,
        })
    SITE_DATA.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    SITE_SCRIPT.write_text("window.HANGUKSA_ANSWERS = " + json.dumps(payload, ensure_ascii=False) + ";\n", encoding="utf-8")

if __name__ == "__main__":
    create_combined_pdf()
    create_site_data()
    print(f"PDF: {OUTPUT}")
