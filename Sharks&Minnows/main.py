from machine import Pin, PWM
import network
import time
from mqtt import MQTTClient 

# motor pin setup
motorA_in1 = Pin(19, Pin.OUT)  
motorA_in2 = Pin(21, Pin.OUT) 
motorB_in1 = Pin(27, Pin.OUT)  
motorB_in2 = Pin(26, Pin.OUT)  

# wifi and mqtt setup
SSID = "Tufts_Robot"  
MQTT_BROKER = "broker.hivemq.com"  
MQTT_PORT = 1883
MQTT_TOPIC = "/movement"

# func to control the left motor (motor a)
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

# func to control the right motor (motor b)
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

# func to stop motors
def stop_motors():
    motorA_control("stop")
    motorB_control("stop")

# func for movement commands
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
        motorA_control("reverse")
        motorB_control("forward")  
        print("Turning left")
    elif command == "right":
        motorA_control("forward")  
        motorB_control("reverse")  
        print("Turning right")
    elif command == "stop":
        stop_motors()
        print("Stopping")

# mqtt handle incoming messages
def mqtt_callback(topic, msg):
    command = msg.decode('utf-8')
    print(f"Received MQTT command: {command}")
    handle_movement(command)

# wifi connection
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('Connecting to Wi-Fi...')
        wlan.connect(SSID)  # no password
        start_time = time.time()
        while not wlan.isconnected():
            if time.time() - start_time > 10:
                raise Exception("Unable to connect to Wi-Fi")
            time.sleep(1)
    print('Wi-Fi connected:', wlan.ifconfig())

# mqtt setup
def setup_mqtt():
    client = MQTTClient("pico_car", MQTT_BROKER, port=MQTT_PORT)
    client.set_callback(mqtt_callback)
    client.connect()
    client.subscribe(MQTT_TOPIC)
    print(f"Subscribed to MQTT topic: {MQTT_TOPIC}")
    return client

# main loop
connect_wifi()
mqtt_client = setup_mqtt()

while True:
    mqtt_client.check_msg()  # check for new messages
    time.sleep(0.1)  # delay to avoid spamming


