import random
import math
import time
from instruments.optical_instrument import OpticalInstrument

class MockOpticalInstrument(OpticalInstrument):

    def __init__(self, address: str = "MOCK::INSTRUMENT", link_loss_db: float = 10.0):
        super().__init__(address)
        self.launch_power_dbm = 0.0
        self.link_loss_db = link_loss_db

    def connect(self, retries: int = 3, delay: float = 1.0):
        for attempt in range(1, retries + 1):
            try:
                if random.random() < 0.2:
                    raise ConnectionError(f"Failed to connect to {self.address}")
                self.connected = True
                print(f"[MOCK] Connected to {self.address} (attempt {attempt})")
                return
            except ConnectionError as e:
                print(f"[MOCK] Connection attempt {attempt} failed: {e}")
                if attempt < retries:
                    time.sleep(delay)
                else:
                    raise ConnectionError(f"Could not connect after {retries} attempts")

    def disconnect(self):
        self.connected = False
        print(f"[MOCK] Disconnected from {self.address}")

    def set_launch_power(self, power_dbm: float):
        if not self.connected:
            raise RuntimeError("Instrument not connected")
        self.launch_power_dbm = power_dbm
        print(f"[MOCK] Launch power set to {power_dbm} dBm")

    def set_link_loss(self, loss_db: float):
        if not self.connected:
            raise RuntimeError("Instrument not connected")
        self.link_loss_db = loss_db
        print(f"[MOCK] Link loss set to {loss_db} dB")

    def measure_osnr(self) -> float:
        if not self.connected:
            raise RuntimeError("Instrument not connected")
        base_osnr = 25.0 + self.launch_power_dbm * 0.8 - self.link_loss_db * 0.5
        noise = random.gauss(0, 0.5)
        return round(base_osnr + noise, 2)

    def measure_ber(self, osnr: float = None) -> float:
        if not self.connected:
            raise RuntimeError("Instrument not connected")
        if osnr is None:
            osnr = self.measure_osnr()
        if osnr < 20:
            ber = random.uniform(0.06, 0.15)
        elif osnr < 22:
            ber = random.uniform(0.001, 0.01)
        else:
            ber = random.uniform(1e-6, 1e-4)
        noise = random.gauss(0, ber * 0.05)
        return max(abs(ber + noise), 1e-15)