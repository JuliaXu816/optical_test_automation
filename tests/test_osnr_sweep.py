import pytest
from mock.mock_instrument import MockOpticalInstrument
from utils.logger import setup_logger
from utils.plotter import plot_osnr_sweep, plot_ber_sweep

LAUNCH_POWERS_DBM = [-5, -3, -1, 0, 1, 3, 5]
LINK_LOSS_DB = 5.0
OSNR_THRESHOLD_DB = 15.0
BER_THRESHOLD = 0.1

logger = setup_logger()

@pytest.fixture
def instrument():
    inst = MockOpticalInstrument(link_loss_db=LINK_LOSS_DB)
    inst.connect()
    logger.info(f"Instrument connected | link_loss={LINK_LOSS_DB} dB")
    yield inst
    inst.disconnect()
    logger.info("Instrument disconnected")

def test_osnr_sweep():
    """Full OSNR sweep across launch powers with plot"""
    inst = MockOpticalInstrument(link_loss_db=LINK_LOSS_DB)
    inst.connect()
    
    osnr_values = []
    failures = []

    for power in LAUNCH_POWERS_DBM:
        inst.set_launch_power(power)
        osnr = inst.measure_osnr()
        osnr_values.append(osnr)
        status = "PASS" if osnr >= OSNR_THRESHOLD_DB else "FAIL"
        logger.info(f"OSNR sweep | power={power} dBm | OSNR={osnr} dB | {status}")
        if osnr < OSNR_THRESHOLD_DB:
            failures.append((power, osnr))

    inst.disconnect()
    plot_osnr_sweep(LAUNCH_POWERS_DBM, osnr_values, OSNR_THRESHOLD_DB)
    
    assert not failures, f"OSNR below threshold at: {failures}"

def test_ber_sweep():
    """Full BER sweep across launch powers with plot"""
    inst = MockOpticalInstrument(link_loss_db=LINK_LOSS_DB)
    inst.connect()

    ber_values = []
    failures = []

    for power in LAUNCH_POWERS_DBM:
        inst.set_launch_power(power)
        ber = inst.measure_ber()
        ber_values.append(ber)
        status = "PASS" if ber <= BER_THRESHOLD else "FAIL"
        logger.info(f"BER sweep | power={power} dBm | BER={ber:.2e} | {status}")
        if ber > BER_THRESHOLD:
            failures.append((power, ber))

    inst.disconnect()
    plot_ber_sweep(LAUNCH_POWERS_DBM, ber_values, BER_THRESHOLD)

    assert not failures, f"BER above threshold at: {failures}"