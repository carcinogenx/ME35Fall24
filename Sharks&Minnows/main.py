from machine import Pin, PWM
import network
import time
from mqtt import MQTTClient  # Ensure you're using the correct MQTT client

# Motor pin setup (adjust pin numbers if needed)
motorA_in1 = Pin(19, Pin.OUT)  # IN1 on H-Bridge for Motor A (left motor)
motorA_in2 = Pin(21, Pin.OUT)  # IN2 on H-Bridge for Motor A (left motor)
motorB_in1 = Pin(27, Pin.OUT)  # IN3 on H-Bridge for Motor B (right motor)
motorB_in2 = Pin(26, Pin.OUT)  # IN4 on H-Bridge for Motor B (right motor)

# Wi-Fi and MQTT setup
SSID = "Tufts_Robot"  # Your Wi-Fi SSID
MQTT_BROKER = "broker.hivemq.com"  # Public MQTT broker
MQTT_PORT = 1883
MQTT_TOPIC = "/movement"

# Function to control the left motor (Motor A)
def motorA_control(direction):
    if direction == "forward":
        motorA_in1.on()
        motorA_in2.off()
    elif direction == "reverse":
        motorA_in1.off()
        motorA_in2.on()
    else:  # Stop
        motorA_in1.off()
        motorA_in2.off()

# Function to control the right motor (Motor B)
def motorB_control(direction):
    if direction == "forward":
        motorB_in1.on()
        motorB_in2.off()
    elif direction == "reverse":
        motorB_in1.off()
        motorB_in2.on()
    else:  # Stop
        motorB_in1.off()
        motorB_in2.off()

# Function to stop both motors
def stop_motors():
    motorA_control("stop")
    motorB_control("stop")

# Function to handle movement commands
def handle_movement(command):
    if command == "forward":
        motorA_control("forward")
        motorB_control("forward")
        print("Moving forward")
    elif command == "backward":
        motorA_control("reverse")
        motorB_control("reverse")
        print("Moving backward")
    elif command == "left":
        motorA_control("reverse")  # Turn left by reversing left motor
        motorB_control("forward")  # Right motor moves forward
        print("Turning left")
    elif command == "right":
        motorA_control("forward")  # Left motor moves forward
        motorB_control("reverse")  # Turn right by reversing right motor
        print("Turning right")
    elif command == "stop":
        stop_motors()
        print("Stopping")

# MQTT callback to handle incoming messages
def mqtt_callback(topic, msg):
    command = msg.decode('utf-8')
    print(f"Received MQTT command: {command}")
    handle_movement(command)

# Wi-Fi connection
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('Connecting to Wi-Fi...')
        wlan.connect(SSID)  # Assuming no password for Tufts_Robot
        start_time = time.time()
        while not wlan.isconnected():
            if time.time() - start_time > 10:
                raise Exception("Unable to connect to Wi-Fi")
            time.sleep(1)
    print('Wi-Fi connected:', wlan.ifconfig())

# MQTT setup
def setup_mqtt():
    client = MQTTClient("pico_car", MQTT_BROKER, port=MQTT_PORT)
    client.set_callback(mqtt_callback)
    client.connect()
    client.subscribe(MQTT_TOPIC)
    print(f"Subscribed to MQTT topic: {MQTT_TOPIC}")
    return client

# Main loop
connect_wifi()
mqtt_client = setup_mqtt()

while True:
    mqtt_client.check_msg()  # Continuously check for new MQTT messages
    time.sleep(0.1)  # Small delay to avoid spamming


