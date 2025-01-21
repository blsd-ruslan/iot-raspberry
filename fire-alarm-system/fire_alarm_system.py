import json  # Using MicroPython's default json module
import time
from enum import Enum

from machine import Pin

from errors import handle_test_failure, handle_measurement_error
from logger import Logger
from flame_sensor import FlameSensor
from wifi_proxy import WiFiProxy

from smoke_sensor import SmokeSensor


class SystemState(Enum):
    NOT_STARTED = 'not_started'
    CALIBRATING = 'calibrating'
    OK = 'ok'
    ALARM = 'alarm'


def load_config():
    with open('config.json') as config_file:
        config = json.load(config_file)  # Using MicroPython's json module
    return config


class FireAlarmSystem:
    def __init__(self):
        self.state = SystemState.NOT_STARTED
        self.config = load_config()
        self.logger = Logger()
        self.wifi_proxy = WiFiProxy(self.config["WIFI"], self.config["MQTT"])
        self.measurement_interval = self.config["MEASUREMENT_INTERVAL"]
        self.calibration_duration = self.config["CALIBRATION_DURATION"]
        self.calibration_end_time = None

        self.smoke_sensor = SmokeSensor(self.config["PINS"]["SMOKE_SENSOR"])
        self.flame_sensor = FlameSensor(self.config["PINS"]["IR_SENSOR"])
        self.alarm_buzzer_pin = Pin(self.config["PINS"]["ALARM_BUZZER"], Pin.OUT)
        self.led_indicator_pin = Pin(self.config["PINS"]["LED_INDICATOR"], Pin.OUT)
        self.logger.info("FireAlarmSystem initialized.")

    def run(self):
        self.logger.info("Starting FireAlarmSystem...")

        # Perform self-tests
        if not self.perform_self_tests():
            self.logger.error("Self-test failed.")
            self.set_system_state("ERROR")
            handle_test_failure(self.wifi_proxy)
            return

        # Initialize system
        self.initialize_system()

        while True:
            self.update_state()
            # self.logger.info("Sleeping for measurement interval.")
            if self.state == SystemState.CALIBRATING:
                # self.publish_state({"info": "Calibration in progress..."})
                # TODO implement logic of sending data to mqtt
            elif self.state == SystemState.OK:
                sensor_data = self.perform_measurements()
                if sensor_data:
                    is_critical = self.analyze_data(sensor_data)
                    if is_critical:
                        self.logger.warning("Critical state detected.")
                        self.handle_critical_state()
                # Replace this with actual sensor readings
                # sensor_data = {"smoke_level": 0.12, "voltage": 3.3}
                # self.publish_state(sensor_data)
                # TODO use lighsleep maybe
            time.sleep(self.measurement_interval)

    def start_calibration(self):
        """Start the calibration phase."""
        self.state = SystemState.CALIBRATING
        self.calibration_end_time = time.time() + self.calibration_duration
        print(f"Calibration started. Will end at {self.calibration_end_time}.")

    def perform_self_tests(self):
        """Perform self-tests on system components."""
        self.logger.info("Performing self-tests...")
        self.set_system_state("SELF_TEST")

        tests = [
            self.test_sensors(),
            self.test_communication(),
            self.test_power()
        ]
        success = all(tests)
        if success:
            self.logger.info("All self-tests passed.")
        else:
            self.logger.error("One or more self-tests failed.")
        return success

    def test_sensors(self):
        """Test the sensors for basic functionality."""
        self.logger.info("Testing sensors...")
        if not self.smoke_sensor.test() or not self.flame_sensor.test():
            self.logger.error("One or more sensors failed.")
            # TODO insert some logic
            return False
        return True

    def test_communication(self):
        """Test communication with the MQTT broker."""
        self.logger.info("Testing communication...")
        try:
            self.wifi_proxy.test_connection()
            return True
        except Exception as e:
            self.logger.error(f"Communication test failed: {e}")
            # TODO insert some logic
            return False

    def test_power(self):
        """Test the power system."""
        self.logger.info("Testing power...")
        # Dummy implementation - Add actual power checks here
        return True

    def initialize_system(self):
        """Initialize sensors and system parameters."""
        self.logger.info("Initializing system...")
        self.start_calibration()
        self.set_initial_thresholds()
        self.set_system_state("RUNNING")
        self.logger.info("System initialized and running.")

    def set_initial_thresholds(self):
        """Set initial thresholds for sensor data analysis."""
        self.logger.info("Setting initial thresholds...")
        # Dummy implementation - Add actual threshold settings here
        pass

    def perform_measurements(self):
        """Get readings from sensors."""
        self.logger.info("Performing measurements...")
        try:
            data = {
                "smoke": self.smoke_sensor.read(),
                "ir": self.flame_sensor.read(),
                "timestamp": time.time()
            }
            self.logger.info(f"Measurement data: {data}")
            return data
        except Exception as e:
            self.logger.error(f"Measurement error: {str(e)}")
            handle_measurement_error(self.wifi_proxy, str(e))
            return None

    def analyze_data(self, data):
        """Analyze sensor data for critical conditions."""
        self.logger.info("Analyzing data...")
        smoke_critical = data["smoke"] > self.config["SMOKE_THRESHOLD"]
        ir_critical = data["ir"] > self.config["IR_THRESHOLD"]
        if smoke_critical or ir_critical:
            self.logger.warning("Critical data thresholds exceeded.")
        return smoke_critical or ir_critical

    def handle_critical_state(self):
        """Handle the critical state (e.g., activate alarm)."""
        self.logger.error("Critical state detected, triggering alarm...")
        print("Critical state detected, triggering alarm...")

    def set_system_state(self, state):
        """Set and publish the system state."""
        self.state = state
        self.logger.info(f"System state updated to: {state}")
        self.wifi_proxy.publish_state({"state": state})

    def update_state(self):
        """Update the system state based on the calibration timer."""
        if self.state == SystemState.CALIBRATING:
            if time.time() >= self.calibration_end_time:
                self.state = SystemState.OK  # Transition to normal operation
                print("Calibration complete. System is now OK.")
