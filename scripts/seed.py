"""
scripts/seed.py
Demo-only: populates the database with realistic mock data so the analysis
queries have something to show. Uses the same db.py functions the real tests
use, so the data is created exactly the way production results would be.

Run from anywhere:  python scripts/seed.py
"""
import sys
import random
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from database import db

random.seed(42)

TEST_SPECS = {
    "OSNR":     (35.0, 2.0, 32.0),
    "BER":      (1e-12, 5e-12, 1e-11),
    "TX_power": (1.0, 0.3, 0.5),
}
PART_NUMBERS = ["QSFP28-100G", "QSFP-DD-400G", "SFP28-25G"]
BATCHES = ["B2026-01", "B2026-02", "B2026-03"]

conn = db.get_connection()

for _ in range(60):
    part = random.choice(PART_NUMBERS)
    batch = random.choice(BATCHES)
    module_id = db.get_or_create_module(conn, part, batch)

    troubled = random.random() < 0.25
    keep_testing = True
    first_run = True
    while keep_testing:
        run_id = db.start_test_run(conn, module_id)
        run_has_fail = False
        for test_name, (mean, std, limit) in TEST_SPECS.items():
            bias = -1.5 * std if (troubled and first_run and test_name != "BER") else 0
            if test_name == "BER":
                value = abs(random.gauss(mean, std)) * (3 if (troubled and first_run) else 1)
                passed = value <= limit
            else:
                value = random.gauss(mean + bias, std)
                passed = value >= limit
            db.record_result(conn, run_id, test_name, round(value, 6), passed)
            if not passed:
                run_has_fail = True
        rn = conn.execute("SELECT run_number FROM test_runs WHERE run_id=?",
                          (run_id,)).fetchone()[0]
        keep_testing = run_has_fail and rn < 3
        first_run = False

for tbl in ("modules", "test_runs", "test_results"):
    n = conn.execute(f"SELECT COUNT(*) FROM {tbl}").fetchone()[0]
    print(f"{tbl}: {n} rows")

conn.close()