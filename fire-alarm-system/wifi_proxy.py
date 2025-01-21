import json
import paho.mqtt.client as mqtt

class WiFiProxy:
    def __init__(self, wifi_config, mqtt_config):
        self.client = None
        self.wifi_connect(wifi_config["ssid"], wifi_config["key"])
        self.mqtt_connect(mqtt_config)

    def wifi_connect(self, ssid, key, timeout=15):
        import network
        import time

        wlan = network.WLAN(network.STA_IF)
        if wlan.isconnected():
            print(f"Already connected to the network: {ssid}")
            print('Network configuration:', wlan.ifconfig())
            return True

        print(f"Connecting to the network {ssid}...")
        wlan.active(True)
        wlan.connect(ssid, key)

        start_time = time.time()
        while not wlan.isconnected():
            # Check if the timeout has been reached
            if time.time() - start_time > timeout:
                print("Error: Connection timed out.")
                return False
            time.sleep(1)  # Small delay between connection checks

        print(f"Successfully connected to the network {ssid}.")
        print('Network configuration:', wlan.ifconfig())
        return True

    def mqtt_connect(self, mqtt_config):
        # Create a new MQTT client instance
        self.client = mqtt.Client(mqtt_config["client_id"])

        # Set MQTT credentials
        self.client.username_pw_set(mqtt_config["user"], mqtt_config["password"])

        # Set callbacks for connection and message handling
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        # Connect to the MQTT broker
        try:
            self.client.connect(mqtt_config["server"], mqtt_config["port"], 60)
            print(f"Connected to MQTT broker {mqtt_config['server']}:{mqtt_config['port']}")
            # Start the loop to process incoming messages
            self.client.loop_start()
        except Exception as e:
            print(f"Error connecting to MQTT broker: {e}")

    def on_connect(self, client, userdata, flags, rc):
        """Callback for MQTT connection"""
        if rc == 0:
            print("Connected to MQTT broker successfully.")
            # Subscribe to the base topic for receiving messages
            client.subscribe(f"{userdata['base_topic']}/cmd")
        else:
            print(f"Failed to connect to MQTT broker. Return code: {rc}")

    def on_message(self, client, userdata, msg):
        """Callback for handling incoming messages"""
        print(f"Message received on topic {msg.topic}: {msg.payload.decode()}")
        # Handle different commands or data here
        if msg.topic.endswith("/cmd"):
            self.handle_commands(msg.payload.decode())
        else:
            self.handle_data(msg.payload.decode())

    def handle_commands(self, command):
        """Handle incoming commands"""
        if command == "shutdown":
            print("Shutting down...")
            self.publish_state("offline")
            self.client.disconnect()
            self.client.loop_stop()

    def handle_data(self, data):
        """Handle incoming data (e.g., sensor data)"""
        print(f"Data received: {data}")

    def publish_error(self, error_data):
        """Publish error message to the MQTT broker"""
        self.client.publish(f"{self.base_topic}/error", json.dumps(error_data), retain=True)

    def publish_state(self, state):
        """Publish state message to the MQTT broker"""
        self.client.publish(f"{self.base_topic}/status", json.dumps({"status": state}), retain=True)

    def test_connection(self):
        """Test MQTT connection"""
        self.client.publish(f"{self.base_topic}/test", "ping")

def load_config():
    with open('config.json') as config_file:
        config = json.load(config_file)  # Using MicroPython's json module
    return config

if __name__ == "__main__":
    config = load_config()
    wifi = WiFiProxy(config["wifi"], config["key"])