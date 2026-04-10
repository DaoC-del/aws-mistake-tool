"""
parser.py – parse a pasted exam-question text block into structured fields.

Supported formats
-----------------
Single correct answer:
    Correct answer: D
    Correct answer: D. AWS Management Console.

Multi-answer (comma / space / no separator):
    Correct answers: A, C
    Correct answers: AC
    Correct answer: A C

Your answer (optional, same flexible formats):
    Your answer: B
    Your answers: A, C
    Your answers: AC

Options:
    A. Some text
    A) Some text
"""

import re
from typing import Dict, List, Optional

_OPTION_RE = re.compile(r"^\s*([A-F])\s*[\.\)]\s*(.+?)\s*$", re.IGNORECASE)
_CORRECT_RE = re.compile(
    r"^\s*Correct\s+answers?\s*[:\-]\s*([A-Fa-f][A-Fa-f,\s]*)\s*$",
    re.IGNORECASE,
)
_YOUR_RE = re.compile(
    r"^\s*Your\s+answers?\s*[:\-]\s*([A-Fa-f][A-Fa-f,\s]*)\s*$",
    re.IGNORECASE,
)


def _parse_letters(raw: str) -> List[str]:
    """Return sorted unique uppercase letters from strings like 'A,C', 'AC', 'A C'."""
    letters = re.findall(r"[A-Fa-f]", raw)
    return sorted(set(l.upper() for l in letters))


def parse_mistake_block(text: str) -> Dict[str, Optional[str]]:
    """
    Parse a pasted question block and return a dict with keys:
        question, option_a..option_f, correct_letters, your_letters, your_correct, raw_text

    Raises ValueError with a descriptive message on parse failure.
    """
    raw = (text or "").strip()
    if not raw:
        raise ValueError("Empty input – paste the question block first.")

    lines = [ln.rstrip() for ln in raw.splitlines() if ln.strip()]
    options: Dict[str, str] = {}
    question_lines: List[str] = []
    correct_letters: List[str] = []
    your_letters: Optional[List[str]] = None

    for ln in lines:
        m_correct = _CORRECT_RE.match(ln)
        if m_correct:
            correct_letters = _parse_letters(m_correct.group(1))
            continue

        m_your = _YOUR_RE.match(ln)
        if m_your:
            your_letters = _parse_letters(m_your.group(1))
            continue

        m_opt = _OPTION_RE.match(ln)
        if m_opt:
            letter = m_opt.group(1).upper()
            options[letter] = m_opt.group(2).strip()
            continue

        question_lines.append(ln.strip())

    question = " ".join(question_lines).strip()

    if not question:
        raise ValueError(
            "Could not parse question text. "
            "Make sure the question appears above the options."
        )
    if not options:
        raise ValueError(
            "Could not parse options. "
            "Use lines like 'A. text' or 'A) text'."
        )
    if not correct_letters:
        raise ValueError(
            "Could not find a 'Correct answer: X' line. "
            "Formats accepted: 'Correct answer: D', 'Correct answers: A,C', 'Correct answers: AC'."
        )

    # Determine correctness when user provided their answer
    your_correct: Optional[int] = None
    if your_letters is not None:
        your_correct = 1 if sorted(your_letters) == sorted(correct_letters) else 0

    return {
        "question": question,
        "option_a": options.get("A"),
        "option_b": options.get("B"),
        "option_c": options.get("C"),
        "option_d": options.get("D"),
        "option_e": options.get("E"),
        "option_f": options.get("F"),
        "correct_letters": ",".join(correct_letters),
        "your_letters": ",".join(your_letters) if your_letters is not None else None,
        "your_correct": your_correct,
        "raw_text": raw,
    }
