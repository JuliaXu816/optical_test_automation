import os
import sys
from datetime import datetime

# Import custom modules
try:
    from mock.mock_instrument import MockOpticalInstrument
    from utils.logger import setup_logger
    from utils.plotter import plot_osnr_sweep, plot_ber_sweep
    from utils.report import generate_html_report
    from utils.config_loader import load_config
except ImportError as e:
    print(f"Import Error: {e}. Check your project structure.")
    sys.exit(1)

def initialize_project():
    """Create necessary directories for logs and reports."""
    required_folders = ['logs', 'reports', 'mock']
    for folder in required_folders:
        os.makedirs(folder, exist_ok=True)

def run_sweep():
    # 1. Initialization
    initialize_project()
    logger = setup_logger()
    
    # 2. Load Configuration
    try:
        config = load_config()
        launch_powers = config["sweep"]["launch_powers_dbm"]
        link_loss = config["instrument"]["link_loss_db"]
        osnr_threshold = config["thresholds"]["osnr_db"]
        ber_threshold = config["thresholds"]["ber"]
    except KeyError as e:
        logger.error(f"Missing configuration key: {e}")
        return

    # 3. Instrument Setup
    inst = MockOpticalInstrument(link_loss_db=link_loss)
    try:
        inst.connect()
    except Exception as e:
        logger.error(f"Instrument connection failed: {e}")
        return

    osnr_values = []
    ber_values = []
    results = []

    # 4. Execute Test Sweep
    print("\n" + "="*70)
    print(f"{'Power (dBm)':<15} {'OSNR (dB)':<15} {'BER':<15} {'Verdict'}")
    print("-" * 70)

    for power in launch_powers:
        # Measurement
        inst.set_launch_power(power)
        osnr = inst.measure_osnr()
        ber = inst.measure_ber(osnr=osnr)
        
        osnr_values.append(osnr)
        ber_values.append(ber)

        # Verdict Logic
        osnr_pass = osnr >= osnr_threshold
        ber_pass = ber <= ber_threshold
        overall_status = "PASS" if (osnr_pass and ber_pass) else "FAIL"

        # Logging and Console Output
        logger.info(f"Power: {power}dBm, OSNR: {osnr}dB, BER: {ber:.2e}, Result: {overall_status}")
        print(f"{power:<15} {osnr:<15.2f} {ber:<15.2e} {overall_status}")
        results.append((power, osnr, ber, overall_status))

    inst.disconnect()

    # 5. Post-Processing & Reporting
    try:
        plot_osnr_sweep(launch_powers, osnr_values, osnr_threshold)
        plot_ber_sweep(launch_powers, ber_values, ber_threshold)
        generate_html_report(results, osnr_threshold, ber_threshold)
    except Exception as e:
        logger.error(f"Post-processing failed: {e}")

    # 6. Final Summary
    print("="*70)
    passed_count = sum(1 for r in results if r[3] == "PASS")
    print(f"Summary: {passed_count}/{len(results)} points passed.")
    print("="*70 + "\n")

if __name__ == "__main__":
    run_sweep()