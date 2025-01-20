import time
import json
from machine import ADC, Pin


class SmokeSensor:
    def __init__(self, config):
        """
        Initialize the SmokeSensor.
        :param config: Configuration dictionary loaded from config.json.
        """
        self.pin = config["SMOKE_SENSOR_PIN"]  # Load pin from config
        self.threshold = config["SMOKE_THRESHOLD"]  # Load threshold from config
        self.sensor = ADC(Pin(self.pin))  # Initialize the ADC on the specified pin

    def calibrate(self):
        """Calibration logic for the sensor."""
        print(f"Calibrating SmokeSensor on pin GP{self.pin}...")
        # Add calibration logic if necessary
        time.sleep(2)
        print("Calibration complete.")

    def read(self):
        """
        Read the sensor value and convert it to a voltage.
        :return: A tuple (value, voltage).
        """
        raw_value = self.sensor.read_u16()  # Read raw analog value (0-65535)
        smoke_sensor_voltage = raw_value * (3.3 / 65535)  # Convert to voltage (0-3.3V)
        return raw_value, smoke_sensor_voltage

    def check_threshold(self):
        """
        Check if the smoke level exceeds the threshold.
        :return: Boolean indicating whether the threshold is exceeded.
        """
        raw_value, _ = self.read()
        return raw_value > self.threshold


# Example Usage
def load_config():
    """Load configuration from config.json."""
    with open("config.json") as config_file:
        return json.load(config_file)


if __name__ == "__main__":
    config = load_config()
    smoke_sensor = SmokeSensor(config)

    smoke_sensor.calibrate()

    while True:
        value, voltage = smoke_sensor.read()
        print(f"Analog Value: {value}, Voltage: {voltage:.2f}V")

        if smoke_sensor.check_threshold():
            print("Warning: Smoke detected!")
        else:
            print("Air quality is normal.")

        time.sleep(1)
