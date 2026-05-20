"""
database/db.py
Thin data-access layer. Tests call these functions to persist results
so test code never contains raw SQL.
"""
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "optical_test.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS modules (
    module_id   INTEGER PRIMARY KEY,
    part_number TEXT    NOT NULL,
    batch_id    TEXT    NOT NULL
);
CREATE TABLE IF NOT EXISTS test_runs (
    run_id     INTEGER PRIMARY KEY,
    module_id  INTEGER NOT NULL,
    timestamp  TEXT    NOT NULL,
    run_number INTEGER NOT NULL,
    FOREIGN KEY (module_id) REFERENCES modules(module_id)
);
CREATE TABLE IF NOT EXISTS test_results (
    result_id  INTEGER PRIMARY KEY,
    run_id     INTEGER NOT NULL,
    test_name  TEXT    NOT NULL,
    condition  REAL,
    value      REAL    NOT NULL,
    pass_fail  TEXT    NOT NULL CHECK (pass_fail IN ('PASS','FAIL')),
    FOREIGN KEY (run_id) REFERENCES test_runs(run_id)
);
"""


def init_db(conn):
    """Create tables if they don't already exist. Safe to call every time."""
    conn.executescript(SCHEMA)
    conn.commit()


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    init_db(conn)  # ensures tables exist — no separate setup step needed
    return conn


def get_or_create_module(conn, part_number, batch_id):
    """Return module_id, inserting the module if it's new."""
    cur = conn.cursor()
    row = cur.execute(
        "SELECT module_id FROM modules WHERE part_number=? AND batch_id=?",
        (part_number, batch_id),
    ).fetchone()
    if row:
        return row[0]
    cur.execute(
        "INSERT INTO modules (part_number, batch_id) VALUES (?,?)",
        (part_number, batch_id),
    )
    conn.commit()
    return cur.lastrowid


def start_test_run(conn, module_id):
    """Create a new test_run row and return its run_id.
    run_number is computed automatically: it's one more than the number
    of runs this module already has (1 = first test, 2 = first retest, ...)."""
    cur = conn.cursor()
    prior = cur.execute(
        "SELECT COUNT(*) FROM test_runs WHERE module_id=?", (module_id,)
    ).fetchone()[0]
    run_number = prior + 1
    cur.execute(
        "INSERT INTO test_runs (module_id, timestamp, run_number) VALUES (?,?,?)",
        (module_id, datetime.now().isoformat(), run_number),
    )
    conn.commit()
    return cur.lastrowid


def record_result(conn, run_id, test_name, value, passed, condition=None):
    """Store one measurement for a run. `condition` holds the sweep
    parameter (e.g. launch power in dBm) when the test is a sweep."""
    conn.execute(
        "INSERT INTO test_results (run_id, test_name, condition, value, pass_fail) "
        "VALUES (?,?,?,?,?)",
        (run_id, test_name, condition, value, "PASS" if passed else "FAIL"),
    )
    conn.commit()