import time
import json
from machine import ADC, Pin
from enum import Enum


class SensorState(Enum):
    NOT_STARTED = 'not_started'
    CALIBRATING = 'calibrating'
    OK = 'ok'
    ALARM = 'alarm'


class SmokeSensor:
    def __init__(self, smoke_sensor_config):
        """
        Initialize the SmokeSensor.
        :param smoke_sensor_config: Configuration dictionary loaded from config.json.
        """
        self.pin = smoke_sensor_config["SMOKE_SENSOR_PIN"]  # Load pin from config
        self.threshold = smoke_sensor_config["SMOKE_THRESHOLD"]  # Load threshold from config
        self.sensor = ADC(Pin(self.pin))  # Initialize the ADC on the specified pin
        self.state = SensorState.NOT_STARTED  # Initial state
        self.calibration_duration = smoke_sensor_config["SMOKE_SENSOR_CALIBRATION_TIME_IN_SECONDS"]
        self.stabilized_value = None  # Variable to store the stabilized value

    def calibrate(self):
        """Calibration logic for the sensor."""
        print(f"Calibrating SmokeSensor on pin GP{self.pin}...")
        self.state = SensorState.CALIBRATING
        start_time = time.time()

        readings = []
        # Calculate the timestamp when we need to start taking the last reading (35 seconds before the end)
        end_time = start_time + self.calibration_duration
        first_reading_time = end_time - 35  # 35 seconds before the end
        second_reading_time = first_reading_time + 10  # 10 seconds after the first
        third_reading_time = second_reading_time + 10  # 10 seconds after the second

        # Take 3 readings with 10 seconds in between, finishing 5 seconds before the calibration ends
        while time.time() < end_time:
            current_time = time.time()
            if first_reading_time <= current_time < second_reading_time:
                raw_value = self.read()
                readings.append(raw_value)
                time.sleep(10)  # Wait for 10 seconds before taking the next reading
            elif second_reading_time <= current_time < third_reading_time:
                raw_value = self.read()
                readings.append(raw_value)
                time.sleep(10)
            elif third_reading_time <= current_time < end_time:
                raw_value = self.read()
                readings.append(raw_value)
                break  # No need to wait after the last reading

        # Calculate the average of the 3 readings
        self.stabilized_value = sum(readings) / len(readings) if readings else 0
        self.state = SensorState.OK  # Once calibrated, set state to OK
        print(f"Calibration complete. Stabilized value: {self.stabilized_value}")

    def read(self):
        """
        Read the sensor value and convert it to a voltage.
        :return: A tuple (value, voltage).
        """
        raw_value = self.sensor.read_u16()  # Read raw analog value (0-65535)
        return raw_value

    def check_threshold(self):
        """
        Check if the smoke level exceeds the threshold.
        :return: Boolean indicating whether the threshold is exceeded.
        """
        raw_value, _ = self.read()
        return raw_value > self.threshold

    def get_state(self):
        """Return the current state of the sensor."""
        if self.state == SensorState.OK:
            if self.check_threshold():
                self.state = SensorState.ALARM
            else:
                self.state = SensorState.OK
        return self.state


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

        state = smoke_sensor.get_state()
        print(f"Sensor State: {state.value}")

        time.sleep(1)
