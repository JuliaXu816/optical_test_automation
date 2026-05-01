import os
from datetime import datetime

def generate_html_report(results: list, osnr_threshold: float, ber_threshold: float):
    """Generate HTML report with sweep results table and plots"""
    
    os.makedirs("reports", exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    passed = sum(1 for r in results if r[3] == "PASS")
    total = len(results)

    rows = ""
    for power, osnr, ber, overall in results:
        color = "green" if overall == "PASS" else "red"
        osnr_color = "green" if osnr >= osnr_threshold else "red"
        ber_color = "green" if ber <= ber_threshold else "red"
        rows += f"""
        <tr>
            <td>{power} dBm</td>
            <td style="color:{osnr_color}">{osnr:.2f} dB</td>
            <td style="color:{ber_color}">{ber:.2e}</td>
            <td style="color:{color}; font-weight:bold">{overall}</td>
        </tr>"""

    html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Optical Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1 {{ color: #333; }}
        table {{ border-collapse: collapse; width: 60%; margin-top: 20px; }}
        th, td {{ border: 1px solid #ddd; padding: 10px; text-align: center; }}
        th {{ background-color: #4472C4; color: white; }}
        tr:nth-child(even) {{ background-color: #f2f2f2; }}
        .summary {{ margin-top: 20px; font-size: 18px; }}
        .plots {{ margin-top: 30px; }}
        img {{ width: 600px; margin-right: 20px; }}
    </style>
</head>
<body>
    <h1>Optical Link Test Report</h1>
    <p>Generated: {timestamp}</p>
    <p>OSNR Threshold: {osnr_threshold} dB | BER Threshold: {ber_threshold:.0e}</p>

    <table>
        <tr>
            <th>Device (Launch Power)</th>
            <th>OSNR</th>
            <th>BER</th>
            <th>Result</th>
        </tr>
        {rows}
    </table>

    <div class="summary">
        Summary: <strong>{passed}/{total}</strong> devices passed
    </div>

    <div class="plots">
        <h2>Sweep Plots</h2>
        <img src="osnr_sweep.png" alt="OSNR Sweep">
        <img src="ber_sweep.png" alt="BER Sweep">
    </div>
</body>
</html>"""

    path = "reports/sweep_report.html"
    with open(path, "w") as f:
        f.write(html)
    print(f"[REPORT] Saved to {path}")