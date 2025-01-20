import time

def handle_test_failure(wifi_proxy):
    """Обрабатывает ошибку теста системы"""
    error_data = {
        "error": "Self-test failure",
        "timestamp": time.time()
    }
    wifi_proxy.publish_error(error_data)

def handle_measurement_error(wifi_proxy, error_message):
    """Обрабатывает ошибку измерений"""
    error_data = {
        "error": "Measurement error",
        "details": error_message,
        "timestamp": time.time()
    }
    wifi_proxy.publish_error(error_data)
