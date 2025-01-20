import time
from machine import Pin


class FlameSensor:
    def __init__(self, config):
        """
        Initialize the FlameSensor.
        :param config: Configuration dictionary loaded from config.json.
        """
        self.pin = config["PINS"]["SMOKE_SENSOR"]  # Load pin from config
        self.sensor = Pin(self.pin, Pin.IN)  # Initialize the digital pin for the sensor

    def measure(self):
        """
        Measure the current state of the flame sensor.
        :return: Boolean indicating whether the flame is detected (True if detected, False otherwise).
        """
        print("Flame sensor measure...")
        time.sleep(1)
        return self.sensor.value()

    def state(self):
        """
        Check the current state of the flame sensor and print the detection result.

        The function uses the `measure` method to determine whether the flame sensor
        detects fire. It then prints the corresponding message ("Fire detected!" or
        "Fire not detected.") and returns the detection result.

        :return: Boolean indicating the state of the flame sensor
                 (True if fire is detected, False otherwise).
        """
        state = self.measure()
        if state:
            print("Fire detected!")
        else:
            print("Fire not detected.")
        time.sleep(1)
        return state