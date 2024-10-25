from machine import Pin, ADC
import time
from mqtt import MQTTClient  

# MQTT settings
MQTT_BROKER = "broker.hivemq.com"
PUB_TOPIC = "/instrument/volume"

# Set up potentiometer
pot = ADC(Pin(3))
pot.atten(ADC.ATTN_11DB) 

# Initialize MQTT 
client = MQTTClient("DahalVolume", MQTT_BROKER)
client.connect()

# publish potentiometer value as volume
def publish_volume():
    pot_value = pot.read()
    volume = int((pot_value / 4095) * 127)  #0-127 is vol range
    print(f"Publishing volume: {volume}")
    client.publish(PUB_TOPIC, str(volume))

# continuously send volume updates
while True:
    publish_volume()
    time.sleep(1) 
