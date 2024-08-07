#Main micropython file

import time
from umqtt_simple import MQTTClient
import network
import machine
import dht

# Define GPIO pins
DHT_PIN = 26
LED_PIN = 12

# Initialize the DHT22 sensor
try:
    dht_sensor = dht.DHT22(machine.Pin(DHT_PIN))
except Exception as e:
    print(f"Error initializing DHT22 sensor: {e}")

# Setup LED pin
led = machine.Pin(LED_PIN, machine.Pin.OUT)
led.value(0)

# MQTT settings
MQTT_SERVER = "broker.hivemq.com"
MQTT_CLIENT_ID = "raspberry_pi_pico_client"  # Unique client ID
TOPIC = "Tempdata"
LIGHTS_TOPIC = "lights"

# Connect to Wi-Fi
def connect_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)

    while not wlan.isconnected():
        print("Connecting to WiFi...")
        time.sleep(1)
    
    print("Connected to Wi-Fi:", wlan.ifconfig())

# Publish temperature and humidity
def publish_data(client):
    try:
        dht_sensor.measure()
        temperature = dht_sensor.temperature()
        humidity = dht_sensor.humidity()

        if temperature is not None and humidity is not None:
            msg = f"{temperature},{humidity}"
            client.publish(TOPIC, msg)
            print(f"Published: {msg}")
        else:
            print("Failed to read from DHT sensor")
    except Exception as e:
        print(f"Error publishing data: {e}")

# MQTT callback function
def mqtt_callback(topic, msg):
    print(f"Message received on topic {topic}: {msg}")
    if msg == b'ON':
        led.value(1)
        print("LED turned ON")
    elif msg == b'OFF':
        led.value(0)
        print("LED turned OFF")

# Main function
def main():
    try:
        connect_wifi("Wokwi-GUEST", "")  # Connect to Wokwi Wi-Fi
        client = MQTTClient(MQTT_CLIENT_ID, MQTT_SERVER)
        client.set_callback(mqtt_callback)
        client.connect()
        client.subscribe(LIGHTS_TOPIC)
        print("Subscribed to:", LIGHTS_TOPIC)
    except Exception as e:
        print(f"Error connecting to Wi-Fi or MQTT: {e}")
        return

    try:
        while True:
            client.check_msg()  # Check for incoming messages
            publish_data(client)  # Publish data periodically
            time.sleep(5)  # Publish every 5 seconds
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Error in main loop: {e}")
    finally:
        client.disconnect()
        print("Disconnected from MQTT")

if __name__ == "__main__":
    main()
