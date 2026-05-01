import pytest
import yaml
import os
from mock.mock_instrument import MockOpticalInstrument
from utils.logger import setup_logger
from utils.plotter import plot_osnr_sweep, plot_ber_sweep

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

# Accessing nested keys as per your config.yaml structure
# Accessing nested keys from config.yaml
LAUNCH_POWERS_DBM = config['sweep']['launch_powers_dbm']
LINK_LOSS_DB = config['instrument']['link_loss_db']
OSNR_THRESHOLD_DB = config['thresholds']['osnr_db'] 
BER_THRESHOLD = config['thresholds']['ber']

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
    
    osnr_values = []
    failures = []

    for power in LAUNCH_POWERS_DBM:
        inst.set_launch_power(power)
        osnr = inst.measure_osnr()
        osnr_values.append(osnr)
        
        # Validation logic synced with config.yaml
        status = "PASS" if osnr >= OSNR_THRESHOLD_DB else "FAIL"
        logger.info(f"OSNR sweep | power={power} dBm | OSNR={osnr} dB | {status}")
        
        if osnr < OSNR_THRESHOLD_DB:
            failures.append((power, osnr))

    inst.disconnect()
    plot_osnr_sweep(LAUNCH_POWERS_DBM, osnr_values, OSNR_THRESHOLD_DB)
    
    assert not failures, f"OSNR failed threshold at: {failures}"

def test_ber_sweep():
    """Execution of BER sweep with pass/fail validation based on config thresholds."""
    inst = MockOpticalInstrument(link_loss_db=LINK_LOSS_DB)
    inst.connect()

    ber_values = []
    failures = []

    for power in LAUNCH_POWERS_DBM:
        inst.set_launch_power(power)
        ber = inst.measure_ber()
        ber_values.append(ber)
        
        # Validation logic synced with config.yaml
        status = "PASS" if ber <= BER_THRESHOLD else "FAIL"
        logger.info(f"BER sweep | power={power} dBm | BER={ber:.2e} | {status}")
        
        if ber > BER_THRESHOLD:
            failures.append((power, ber))

    inst.disconnect()
    plot_ber_sweep(LAUNCH_POWERS_DBM, ber_values, BER_THRESHOLD)

    assert not failures, f"BER failed threshold at: {failures}"