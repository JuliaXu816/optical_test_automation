Optical Test Automation Framework
This project provides an automated sweep testing framework for evaluating Optical Signal-to-Noise Ratio (OSNR) and Bit Error Rate (BER) performance in optical links. It uses a mock instrument interface to simulate real-world hardware testing scenarios.

Key Features
Automated Sweeps: Executes power sweeps across a defined range of launch powers.

Dynamic Configuration: All test parameters (thresholds, link loss, sweep ranges) are managed via a nested config.yaml file, separating test logic from hardware specifications.

Data Visualization: Automatically generates OSNR and BER performance plots (log scale) for quick margin analysis.

Professional Reporting: Generates a standalone HTML test report summarizing Pass/Fail results for each test point.

CI/CD Integration: Includes a GitHub Actions workflow for automated testing and code validation on every push.

Project Structure
tests/: Contains pytest scripts for OSNR and BER validation.

mock/: Simulated optical instrument drivers.

utils/: Logging, plotting, and report generation utilities.

config.yaml: Centralized configuration for all test parameters.

reports/: Output directory for HTML reports and PNG plots.

Setup & Execution
Prerequisites
Python 3.10+

Dependencies: pytest, pyyaml, matplotlib, jinja2

Running Tests
To run the automated test suite locally:

Bash
$env:PYTHONPATH += ";$(pwd)"; pytest -s tests/test_osnr_sweep.py
Configuration
Modify config.yaml to adjust test limits:

YAML
thresholds:
  osnr_db: 15.0
  ber: 0.15
Sample Output
The framework generates a visual summary of the link performance:

OSNR Sweep Plot: Visualizes signal quality against the defined threshold.

BER Sweep Plot: Displays bit error rate trends using a logarithmic scale.

HTML Report: A concise table-based summary.
