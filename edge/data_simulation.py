# Simulates sensor readings for testing and development purposes. 
# This file generates synthetic motion data that mimics the expected output from the actual sensor, 
# allowing developers to test the system without requiring physical hardware.


import time
import numpy as np
from datetime import datetime, timezone


class DataSimulation:

    def __init__(self, mode="idle", noise_std=0.05):
        self.mode = mode
        self.noise_std = noise_std
        self.start_time = time.monotonic()

    def set_mode(self, mode: str):
        if mode not in ("idle", "shaking", "walking"):
            raise ValueError(f"Invalid mode: {mode}")

        self.mode = mode

    def _idle(self) -> np.ndarray:
        return np.zeros(3)

    def _shaking(self) -> np.ndarray:
        return np.random.uniform(-5.0, 5.0, size=3)

    def _walking(self, t: float) -> np.ndarray:
        frequency = 1.8
        phase = 2 * np.pi * frequency * t

        amplitude = np.random.uniform(0.8, 1.2)

        x = 2.0 + amplitude * np.sin(phase)
        y = 0.2 * np.sin(phase / 2)
        z = 0.5 * np.cos(phase)

        return np.array([x, y, z])

    def generate_sample(self, mode) -> dict:
        t = time.monotonic() - self.start_time

        if mode not in ("idle", "shaking", "walking"):
            raise ValueError(f"Invalid mode: {mode}")
        self.mode = mode

        match self.mode:
            case "idle":
                signal = self._idle()
            case "shaking":
                signal = self._shaking()
            case "walking":
                signal = self._walking(t)
            case _:
                raise ValueError(f"Invalid mode: {self.mode}")

        noise = np.random.normal(
            loc=0.0,
            scale=self.noise_std,
            size=3
        )

        signal = signal + noise

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "x": float(signal[0]),
            "y": float(signal[1]),
            "z": float(signal[2]),
            "label": self.mode
        }


if __name__ == "__main__":
    simulator = DataSimulation(mode="walking")
    sample_rate = 50

    try:
        while True:
            data = simulator.read()
            print(data)
            time.sleep(1 / sample_rate)

    except KeyboardInterrupt:
        print("Simulation stopped.")

