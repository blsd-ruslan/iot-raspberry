class SensorError(Exception):
    """Custom exception for sensor-related errors."""
    pass


class BaseSensor:
    def __init__(self, name, pin):
        self.name = name
        self.pin = pin
        self.value = None

    def read(self):
        """Read the sensor value (to be implemented in subclasses)."""
        raise NotImplementedError("Subclasses must implement the 'read' method.")

    def calibrate(self):
        """Calibrate the sensor if needed."""
        pass
