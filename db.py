# -*- coding: utf-8 -*-
"""사용자별 풀이 기록 · 오답노트 · 북마크를 SQLite에 저장한다.

Streamlit Community Cloud의 파일 시스템은 앱이 재시작되거나 재배포되면 초기화될 수 있다.
"""
import os
import sqlite3
from contextlib import closing
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "quiz.db")

# 오답노트에 있는 문제를 이 횟수만큼 연속으로 맞히면 오답노트에서 빠진다.
CLEAR_STREAK = 2

_SCHEMA = """
CREATE TABLE IF NOT EXISTS attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user TEXT NOT NULL,
    qid TEXT NOT NULL,
    correct INTEGER NOT NULL,
    ts TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_attempts_user ON attempts(user);

CREATE TABLE IF NOT EXISTS wrong_notes (
    user TEXT NOT NULL,
    qid TEXT NOT NULL,
    wrong_count INTEGER NOT NULL DEFAULT 0,
    streak INTEGER NOT NULL DEFAULT 0,
    memo TEXT NOT NULL DEFAULT '',
    active INTEGER NOT NULL DEFAULT 1,
    last_wrong TEXT,
    PRIMARY KEY (user, qid)
);

CREATE TABLE IF NOT EXISTS bookmarks (
    user TEXT NOT NULL,
    qid TEXT NOT NULL,
    ts TEXT NOT NULL,
    PRIMARY KEY (user, qid)
);
"""


def _connect():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.executescript(_SCHEMA)
    return conn


def _now():
    return datetime.now().isoformat(timespec="seconds")


def record_answer(user, qid, correct):
    """풀이 한 건을 기록하고 오답노트를 갱신한다.

    틀리면 오답노트에 넣거나(다시) 활성화하고 연속 정답을 0으로 되돌린다.
    오답노트에 있는 문제를 맞히면 연속 정답을 올리고, CLEAR_STREAK에 닿으면 오답노트에서 뺀다.
    """
    now = _now()
    with closing(_connect()) as conn, conn:
        conn.execute(
            "INSERT INTO attempts (user, qid, correct, ts) VALUES (?, ?, ?, ?)",
            (user, qid, int(correct), now),
        )
        if not correct:
            conn.execute(
                """
                INSERT INTO wrong_notes (user, qid, wrong_count, streak, active, last_wrong)
                VALUES (?, ?, 1, 0, 1, ?)
                ON CONFLICT(user, qid) DO UPDATE SET
                    wrong_count = wrong_count + 1, streak = 0, active = 1, last_wrong = excluded.last_wrong
                """,
                (user, qid, now),
            )
        else:
            conn.execute(
                """
                UPDATE wrong_notes
                SET streak = streak + 1,
                    active = CASE WHEN streak + 1 >= ? THEN 0 ELSE 1 END
                WHERE user = ? AND qid = ? AND active = 1
                """,
                (CLEAR_STREAK, user, qid),
            )


def wrong_notes(user):
    with closing(_connect()) as conn:
        rows = conn.execute(
            "SELECT * FROM wrong_notes WHERE user = ? AND active = 1 "
            "ORDER BY wrong_count DESC, last_wrong DESC",
            (user,),
        ).fetchall()
    return [dict(r) for r in rows]


def save_memo(user, qid, memo):
    with closing(_connect()) as conn, conn:
        conn.execute("UPDATE wrong_notes SET memo = ? WHERE user = ? AND qid = ?", (memo, user, qid))


def remove_wrong(user, qid):
    with closing(_connect()) as conn, conn:
        conn.execute("UPDATE wrong_notes SET active = 0 WHERE user = ? AND qid = ?", (user, qid))


def bookmarks(user):
    with closing(_connect()) as conn:
        rows = conn.execute("SELECT qid FROM bookmarks WHERE user = ? ORDER BY ts DESC", (user,)).fetchall()
    return [r["qid"] for r in rows]


def toggle_bookmark(user, qid):
    with closing(_connect()) as conn, conn:
        deleted = conn.execute("DELETE FROM bookmarks WHERE user = ? AND qid = ?", (user, qid)).rowcount
        if not deleted:
            conn.execute("INSERT INTO bookmarks (user, qid, ts) VALUES (?, ?, ?)", (user, qid, _now()))


def attempts(user):
    with closing(_connect()) as conn:
        rows = conn.execute("SELECT qid, correct, ts FROM attempts WHERE user = ? ORDER BY ts", (user,)).fetchall()
    return [dict(r) for r in rows]
