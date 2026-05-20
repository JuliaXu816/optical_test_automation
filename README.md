# Optical Test Automation Framework

This project provides an automated sweep testing framework for evaluating
Optical Signal-to-Noise Ratio (OSNR) and Bit Error Rate (BER) performance in
optical links. It uses a mock instrument interface to simulate real-world
hardware testing scenarios, persists results to a structured database, and
turns raw measurements into actionable quality insight.

## Key Features

- **Automated Sweeps:** Executes power sweeps across a defined range of launch powers.
- **Dynamic Configuration:** All test parameters (thresholds, link loss, sweep ranges) are managed via a nested `config.yaml` file, separating test logic from hardware specifications.
- **Data Persistence & Analysis:** Test results are stored in a normalized SQLite database (instead of loose files), enabling cross-run and cross-batch analysis — failure Pareto, per-batch yield, and retest tracking. 
- **Data Visualization:** Automatically generates OSNR and BER performance plots (log scale) for quick margin analysis.
- **Professional Reporting:** Generates a standalone HTML test report summarizing Pass/Fail results for each test point.
- **CI/CD Integration:** Includes a GitHub Actions workflow for automated testing and code validation on every push.

## Project Structure

- `tests/` — pytest scripts for OSNR and BER validation.
- `mock/` — simulated optical instrument drivers.
- `utils/` — logging, plotting, and report generation utilities.
- `database/` — SQLite schema and a data-access layer (`db.py`) that keeps SQL out of the test code; tables self-initialize on first connection. 
- `analysis/` — analytical SQL queries that turn stored results into engineering insight. 
- `scripts/` — utility scripts, including a seed generator for demo data. 
- `config.yaml` — centralized configuration for all test parameters.
- `reports/` — output directory for HTML reports and PNG plots.

## Setup & Execution

### Prerequisites
- Python 3.10+
- Dependencies: `pytest`, `pyyaml`, `matplotlib`, `jinja2`

### Running Tests
To run the automated test suite locally:

```bash
$env:PYTHONPATH += ";$(pwd)"; pytest -s tests/test_osnr_sweep.py
```

Running the tests automatically persists each measurement to the database, so
no separate setup step is required.

### Configuration
Modify `config.yaml` to adjust test limits:

```yaml
thresholds:
  osnr_db: 15.0
  ber: 0.15
```

## Data Analysis *(← NEW SECTION)*

Beyond pass/fail, the framework supports engineering analysis of accumulated
test data. The database uses three normalized tables — `modules` (unit under
test), `test_runs` (one row per execution, with an auto-incrementing
`run_number` distinguishing first tests from retests), and `test_results` (one
row per measurement, tagged with sweep condition and verdict).

The queries in `analysis/queries.py` produce:

- **Failure Pareto** — failure modes ranked by frequency, to prioritize root-cause effort.
- **Per-batch fail rate** — a JOIN across all three tables that surfaces batches with abnormal yield.
- **Process spread** — per-part mean / min / max OSNR as inputs to Cpk capability analysis.
- **Marginal-unit detection** — a subquery that finds units which failed on first test but passed on retest, flagging low-margin parts that pass QA but carry field-reliability risk.

To populate demo data and run the analysis:

```bash
python scripts/seed.py        # generate mock data
python analysis/queries.py    # print the analyses
```

## Sample Output

The framework generates a visual summary of the link performance:

- **OSNR Sweep Plot:** visualizes signal quality against the defined threshold.
- **BER Sweep Plot:** displays bit error rate trends using a logarithmic scale.
- **HTML Report:** a concise table-based summary.
