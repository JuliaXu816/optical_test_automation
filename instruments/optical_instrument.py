class OpticalInstrument:
    """Base class representing a real optical instrument (e.g. JDSU, Agilent OSA)"""

    def __init__(self, address: str):
        self.address = address
        self.connected = False

    def connect(self):
        raise NotImplementedError("Subclass must implement connect()")

    def disconnect(self):
        raise NotImplementedError("Subclass must implement disconnect()")

    def measure_osnr(self) -> float:
        raise NotImplementedError("Subclass must implement measure_osnr()")

    def measure_ber(self) -> float:
        raise NotImplementedError("Subclass must implement measure_ber()")