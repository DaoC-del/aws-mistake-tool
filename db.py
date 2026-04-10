"""
db.py – SQLite persistence layer for the AWS mistake tracker.
"""

import sqlite3
from typing import Any, Dict, List, Optional

SCHEMA = """
CREATE TABLE IF NOT EXISTS mistakes (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    exam            TEXT    NOT NULL DEFAULT 'CLF-C02',
    domain          TEXT,
    topic           TEXT,
    tags            TEXT,
    reason          TEXT,

    question        TEXT    NOT NULL,
    option_a        TEXT,
    option_b        TEXT,
    option_c        TEXT,
    option_d        TEXT,
    option_e        TEXT,
    option_f        TEXT,

    correct_letters TEXT    NOT NULL,
    your_letters    TEXT,
    your_correct    INTEGER,

    raw_text        TEXT    NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_mistakes_exam       ON mistakes(exam);
CREATE INDEX IF NOT EXISTS idx_mistakes_domain     ON mistakes(domain);
CREATE INDEX IF NOT EXISTS idx_mistakes_created_at ON mistakes(created_at);
"""

_INSERT_COLS = [
    "exam", "domain", "topic", "tags", "reason",
    "question",
    "option_a", "option_b", "option_c", "option_d", "option_e", "option_f",
    "correct_letters", "your_letters", "your_correct",
    "raw_text",
]


def get_conn(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA)
    conn.commit()


def insert_mistake(conn: sqlite3.Connection, row: Dict[str, Any]) -> int:
    placeholders = ",".join(["?"] * len(_INSERT_COLS))
    sql = f"INSERT INTO mistakes ({','.join(_INSERT_COLS)}) VALUES ({placeholders})"
    values = [row.get(c) for c in _INSERT_COLS]
    cur = conn.execute(sql, values)
    conn.commit()
    return int(cur.lastrowid)

# ---------------------------------------------------------------------------
# Query helpers – fully parametric: no user data ever enters the SQL string
# ---------------------------------------------------------------------------

def _filter_params(
    exam: Optional[str],
    domain: Optional[str],
    tag: Optional[str],
    keyword: Optional[str],
    only_incorrect: bool,
    only_correct: bool,
) -> List[Any]:
    """Return the parameter list that matches _FILTER_SQL below."""
    k = f"%{keyword.lower()}%" if keyword else None
    t = f"%{tag.lower()}%" if tag else None
    return [
        exam, exam,                 # (? IS NULL OR exam = ?)
        domain, domain, domain,     # (? IS NULL OR ? = 'ALL' OR domain = ?)
        t, t,                       # (? IS NULL OR LOWER(tags) LIKE ?)
        k, k, k, k, k,             # (? IS NULL OR keyword LIKE in 4 columns)
        int(only_incorrect),        # (? = 0 OR your_correct = 0)
        int(only_correct),          # (? = 0 OR your_correct = 1)
    ]


# Fixed SQL fragment – no string interpolation; all conditions are optional
# via the "? IS NULL" idiom so active filters are controlled only by params.
_FILTER_SQL = (
    "WHERE (? IS NULL OR exam = ?) "
    "AND (? IS NULL OR ? = 'ALL' OR domain = ?) "
    "AND (? IS NULL OR LOWER(tags) LIKE ?) "
    "AND (? IS NULL OR ("
    "LOWER(question) LIKE ? OR LOWER(topic) LIKE ? "
    "OR LOWER(reason) LIKE ? OR LOWER(raw_text) LIKE ?)) "
    "AND (? = 0 OR your_correct = 0) "
    "AND (? = 0 OR your_correct = 1)"
)


def count_mistakes(
    conn: sqlite3.Connection,
    exam: Optional[str] = None,
    domain: Optional[str] = None,
    tag: Optional[str] = None,
    keyword: Optional[str] = None,
    only_incorrect: bool = False,
    only_correct: bool = False,
) -> int:
    params = _filter_params(exam, domain, tag, keyword, only_incorrect, only_correct)
    row = conn.execute(
        "SELECT COUNT(*) AS c FROM mistakes " + _FILTER_SQL, params
    ).fetchone()
    return int(row["c"])


def list_mistakes(
    conn: sqlite3.Connection,
    limit: int,
    offset: int,
    exam: Optional[str] = None,
    domain: Optional[str] = None,
    tag: Optional[str] = None,
    keyword: Optional[str] = None,
    only_incorrect: bool = False,
    only_correct: bool = False,
) -> List[sqlite3.Row]:
    params = _filter_params(exam, domain, tag, keyword, only_incorrect, only_correct)
    sql = (
        "SELECT id, created_at, exam, domain, topic, tags, reason, "
        "question, correct_letters, your_letters, your_correct "
        "FROM mistakes " + _FILTER_SQL
        + " ORDER BY datetime(created_at) DESC, id DESC LIMIT ? OFFSET ?"
    )
    return conn.execute(sql, params + [limit, offset]).fetchall()


def get_mistake(conn: sqlite3.Connection, mistake_id: int) -> Optional[sqlite3.Row]:
    return conn.execute(
        "SELECT * FROM mistakes WHERE id = ?", [mistake_id]
    ).fetchone()


def distinct_exams(conn: sqlite3.Connection) -> List[str]:
    rows = conn.execute(
        "SELECT DISTINCT exam FROM mistakes WHERE exam IS NOT NULL ORDER BY exam"
    ).fetchall()
    return [r["exam"] for r in rows]
