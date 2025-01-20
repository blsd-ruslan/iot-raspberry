class Logger:

    def __init__(self):
        """Initialize the logger."""
        pass

    def log(self, level: str, message: str):
        """Log a message at the given level."""
        pass

    def info(self, message: str):
        """Log an informational message."""
        pass

    def warning(self, message: str):
        """Log a warning message."""
        pass

    def error(self, message: str):
        """Log an error message."""
        pass

    def _format_message(self, level: str, message: str) -> str:
        """Format the log message."""
        pass
