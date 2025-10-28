
class MockGPIO:
    BCM = 'BCM'
    OUT = 'OUT'
    IN = 'IN'
    _pins = {}

    @classmethod
    def setwarnings(cls, flag):
        print(f"[GPIO] Warnings set to {flag}")

    @classmethod
    def setmode(cls, mode):
        print(f"[GPIO] Mode set to {mode}")

    @classmethod
    def setup(cls, pins, mode):
        if isinstance(pins, int):
            pins = [pins]
        for pin in pins:
            cls._pins[pin] = 0
            print(f"[GPIO] Pin {pin} set as {mode}")

    @classmethod
    def output(cls, pin, value):
        cls._pins[pin] = value
        print(f"[GPIO] Output set: Pin {pin} = {value}")

    @classmethod
    def input(cls, pin):
        val = cls._pins.get(pin, 0)
        print(f"[GPIO] Reading input from Pin {pin}: {val}")
        return val
