import sqlite3
from pathlib import Path

# Same location db.py uses: always database/optical_test.db,
# regardless of which directory you run this from.
DB_PATH = Path(__file__).parent / "optical_test.db"

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.executescript("""
DROP TABLE IF EXISTS test_results;
DROP TABLE IF EXISTS test_runs;
DROP TABLE IF EXISTS modules;

CREATE TABLE modules (
    module_id   INTEGER PRIMARY KEY,
    part_number TEXT    NOT NULL,
    batch_id    TEXT    NOT NULL
);

CREATE TABLE test_runs (
    run_id     INTEGER PRIMARY KEY,
    module_id  INTEGER NOT NULL,
    timestamp  TEXT    NOT NULL,
    run_number INTEGER NOT NULL,          -- 1 = first test, 2 = first retest, ...
    FOREIGN KEY (module_id) REFERENCES modules(module_id)
);

CREATE TABLE test_results (
    result_id  INTEGER PRIMARY KEY,
    run_id     INTEGER NOT NULL,
    test_name  TEXT    NOT NULL,          -- 'OSNR', 'BER', 'TX_power', ...
    condition  REAL,                      -- e.g. launch power in dBm for a sweep point
    value      REAL    NOT NULL,
    pass_fail  TEXT    NOT NULL CHECK (pass_fail IN ('PASS','FAIL')),
    FOREIGN KEY (run_id) REFERENCES test_runs(run_id)
);
""")

conn.commit()
conn.close()
print("Schema created: optical_test.db")