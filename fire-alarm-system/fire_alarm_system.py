import time
from pydantic import json
from wifi_proxy import WiFiProxy
from baseSensor import read_smoke_sensor, read_ir_sensor, SensorError
from errors import handle_test_failure, handle_measurement_error
from logger import Logger
from machine import Pin


def load_config():
    with open('config.json') as config_file:
        config = json.load(config_file)
    return config


class FireAlarmSystem:
    def __init__(self):
        self.config = load_config()
        self.logger = Logger()
        self.wifi_proxy = WiFiProxy()
        self.system_state = "INIT"
        self.measurement_interval = self.config["MEASUREMENT_INTERVAL"]
        self.normalization_duration = self.config["NORMALIZATION_DURATION"]  # Time to wait for sensors to normalize

        self.smoke_sensor_pin = Pin(self.config["PINS"]["SMOKE_SENSOR"], Pin.IN)
        self.ir_sensor_pin = Pin(self.config["PINS"]["IR_SENSOR"], Pin.IN)
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

        # Normalize sensors
        if not self.normalize_sensors():
            self.logger.error("Sensor normalization failed.")
            self.set_system_state("ERROR")
            return

        # Initialize system
        self.initialize_system()

        # Main operation loop
        while True:
            self.logger.info("Sleeping for measurement interval.")
            time.sleep(self.measurement_interval)

            # Take measurements
            sensor_data = self.perform_measurements()

            # Analyze if we got measurements
            if sensor_data:
                is_critical = self.analyze_data(sensor_data)
                if is_critical:
                    self.logger.warning("Critical state detected.")
                    self.handle_critical_state()

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
        # Dummy implementation - Add actual sensor checks here
        return True

    def test_communication(self):
        """Test communication with the MQTT broker."""
        self.logger.info("Testing communication...")
        # Dummy implementation - Add actual communication checks here
        try:
            self.wifi_proxy.test_connection()
            return True
        except Exception as e:
            self.logger.error(f"Communication test failed: {e}")
            return False

    def test_power(self):
        """Test the power system."""
        self.logger.info("Testing power...")
        # Dummy implementation - Add actual power checks here
        return True

    def normalize_sensors(self):
        """Wait for sensors to stabilize before the system becomes operational."""
        self.logger.info("Normalizing sensors...")
        self.set_system_state("INITIALIZING")

        start_time = time.time()
        while time.time() - start_time < self.normalization_duration:
            smoke = read_smoke_sensor()
            self.logger.info(f"Smoke sensor reading during normalization: {smoke}")
            # Add additional conditions if needed for stabilization
            time.sleep(1)

        self.logger.info("Sensors normalized.")
        return True

    def initialize_system(self):
        """Initialize sensors and system parameters."""
        self.logger.info("Initializing system...")
        self.calibrate_sensors()
        self.set_initial_thresholds()
        self.set_system_state("RUNNING")
        self.logger.info("System initialized and running.")

    def calibrate_sensors(self):
        """Calibrate sensors before starting the system."""
        self.logger.info("Calibrating sensors...")
        # Dummy implementation - Add actual calibration logic here
        pass

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
                "smoke": read_smoke_sensor(),
                "ir": read_ir_sensor(),
                "timestamp": time.time()
            }
            self.logger.info(f"Measurement data: {data}")
            return data
        except SensorError as e:
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
        self.system_state = state
        self.logger.info(f"System state updated to: {state}")
        self.wifi_proxy.publish_state({"state": state})

