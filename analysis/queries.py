import sqlite3

from pathlib import Path
DB_PATH = Path(__file__).parent.parent / "database" / "optical_test.db"
conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

def show(title, sql):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)
    rows = cur.execute(sql).fetchall()
    if not rows:
        print("(no rows)")
        return
    cols = rows[0].keys()
    print(" | ".join(cols))
    for r in rows[:15]:
        print(" | ".join(str(r[c]) for c in cols))


# Q1 — SELECT + WHERE: every FAIL result. The basics.
show("Q1: All failing test results",
"""
SELECT run_id, test_name, value, pass_fail
FROM test_results
WHERE pass_fail = 'FAIL';
""")

# Q2 — GROUP BY + COUNT: Pareto of failure modes.
# This IS the Pareto chart in SQL form.
show("Q2: Pareto — failures by test type (most common first)",
"""
SELECT test_name,
       COUNT(*) AS fail_count
FROM test_results
WHERE pass_fail = 'FAIL'
GROUP BY test_name
ORDER BY fail_count DESC;
""")

# Q3 — JOIN: connect failures back to which batch they came from.
show("Q3: Fail rate by batch (JOIN across all 3 tables)",
"""
SELECT m.batch_id,
       COUNT(*)                                        AS total_tests,
       SUM(CASE WHEN tr.pass_fail = 'FAIL' THEN 1 ELSE 0 END) AS fails,
       ROUND(100.0 * SUM(CASE WHEN tr.pass_fail='FAIL' THEN 1 ELSE 0 END)
             / COUNT(*), 1)                            AS fail_pct
FROM modules m
JOIN test_runs   r  ON r.module_id = m.module_id
JOIN test_results tr ON tr.run_id   = r.run_id
GROUP BY m.batch_id
ORDER BY fail_pct DESC;
""")

# Q4 — Cpk-style stats: mean & spread of OSNR per part number.
# AVG + a manual std-dev gives you process capability inputs.
show("Q4: OSNR distribution per part number (Cpk inputs)",
"""
SELECT m.part_number,
       COUNT(tr.value)            AS n,
       ROUND(AVG(tr.value), 3)    AS mean_osnr,
       ROUND(MIN(tr.value), 3)    AS min_osnr,
       ROUND(MAX(tr.value), 3)    AS max_osnr
FROM modules m
JOIN test_runs    r  ON r.module_id = m.module_id
JOIN test_results tr ON tr.run_id   = r.run_id
WHERE tr.test_name = 'OSNR'
GROUP BY m.part_number;
""")

# Q5 — the hard one: modules that FAILED on run 1 but PASSED on a later run.
# Uses run_number + a subquery. This is the "borderline / marginal unit" finder.
show("Q5: Modules that failed first test but passed on retest",
"""
SELECT DISTINCT m.module_id, m.part_number
FROM modules m
WHERE m.module_id IN (
        SELECT r.module_id
        FROM test_runs r
        JOIN test_results tr ON tr.run_id = r.run_id
        WHERE r.run_number = 1 AND tr.pass_fail = 'FAIL'
      )
  AND m.module_id IN (
        SELECT r.module_id
        FROM test_runs r
        WHERE r.run_number > 1
          AND r.run_id NOT IN (
              SELECT run_id FROM test_results WHERE pass_fail = 'FAIL'
          )
      );
""")

conn.close()