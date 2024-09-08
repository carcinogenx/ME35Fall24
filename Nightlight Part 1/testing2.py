from mqtt import MQTTClient  # Make sure this import works

def test_mqtt_client():
    try:
        # Create the MQTT client
        client = MQTTClient("pico_nightlight", "broker.hivemq.com")
        
        if client is None:
            print("Failed to create MQTT client")
        else:
            client.connect()
            print("Successfully connected to MQTT broker")
            client.disconnect()
            print("Disconnected from MQTT broker")
    except Exception as e:
        print(f"Error during MQTT client test: {e}")

test_mqtt_client()