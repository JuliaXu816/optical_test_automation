import pytest
import yaml
import os
from mock.mock_instrument import MockOpticalInstrument
from utils.logger import setup_logger
from utils.plotter import plot_osnr_sweep, plot_ber_sweep
from database import db  # NEW: data-access layer


def load_config():
    """
    Dynamically loads the configuration from the root directory.
    Ensures absolute path resolution for compatibility with local and CI environments.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(base_dir, 'config.yaml')

    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


# Load configuration and map nested keys to variables
config = load_config()

LAUNCH_POWERS_DBM = config['sweep']['launch_powers_dbm']
LINK_LOSS_DB = config['instrument']['link_loss_db']
OSNR_THRESHOLD_DB = config['thresholds']['osnr_db']
BER_THRESHOLD = config['thresholds']['ber']

# NEW: identify which module/build is under test. Pull from config if present,
# otherwise fall back to sensible defaults so the test still runs.
PART_NUMBER = config.get('module', {}).get('part_number', 'QSFP28-100G')
BATCH_ID = config.get('module', {}).get('batch_id', 'DEV')

logger = setup_logger()


@pytest.fixture
def instrument():
    """Fixture to manage instrument connection lifecycle using config parameters."""
    inst = MockOpticalInstrument(link_loss_db=LINK_LOSS_DB)
    inst.connect()
    logger.info(f"Instrument connected | link_loss={LINK_LOSS_DB} dB")
    yield inst
    inst.disconnect()
    logger.info("Instrument disconnected")


def test_osnr_sweep():
    """Execution of OSNR sweep with pass/fail validation based on config thresholds."""
    inst = MockOpticalInstrument(link_loss_db=LINK_LOSS_DB)
    inst.connect()

    # NEW: open a DB connection and register this test run
    conn = db.get_connection()
    module_id = db.get_or_create_module(conn, PART_NUMBER, BATCH_ID)
    run_id = db.start_test_run(conn, module_id)

    osnr_values = []
    failures = []

    for power in LAUNCH_POWERS_DBM:
        inst.set_launch_power(power)
        osnr = inst.measure_osnr()
        osnr_values.append(osnr)

        status = "PASS" if osnr >= OSNR_THRESHOLD_DB else "FAIL"
        logger.info(f"OSNR sweep | power={power} dBm | OSNR={osnr} dB | {status}")

        # NEW: persist each sweep point (power is the condition)
        db.record_result(conn, run_id, "OSNR", osnr,
                         passed=(osnr >= OSNR_THRESHOLD_DB), condition=power)

        if osnr < OSNR_THRESHOLD_DB:
            failures.append((power, osnr))

    conn.close()  # NEW
    inst.disconnect()
    plot_osnr_sweep(LAUNCH_POWERS_DBM, osnr_values, OSNR_THRESHOLD_DB)

    assert not failures, f"OSNR failed threshold at: {failures}"


def test_ber_sweep():
    """Execution of BER sweep with pass/fail validation based on config thresholds."""
    inst = MockOpticalInstrument(link_loss_db=LINK_LOSS_DB)
    inst.connect()

    # NEW: register this run
    conn = db.get_connection()
    module_id = db.get_or_create_module(conn, PART_NUMBER, BATCH_ID)
    run_id = db.start_test_run(conn, module_id)

    ber_values = []
    failures = []

    for power in LAUNCH_POWERS_DBM:
        inst.set_launch_power(power)
        ber = inst.measure_ber()
        ber_values.append(ber)

        status = "PASS" if ber <= BER_THRESHOLD else "FAIL"
        logger.info(f"BER sweep | power={power} dBm | BER={ber:.2e} | {status}")

        # NEW: persist each sweep point
        db.record_result(conn, run_id, "BER", ber,
                         passed=(ber <= BER_THRESHOLD), condition=power)

        if ber > BER_THRESHOLD:
            failures.append((power, ber))

    conn.close()  # NEW
    inst.disconnect()
    plot_ber_sweep(LAUNCH_POWERS_DBM, ber_values, BER_THRESHOLD)

    assert not failures, f"BER failed threshold at: {failures}"