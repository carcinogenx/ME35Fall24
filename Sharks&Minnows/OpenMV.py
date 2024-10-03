import sensor, image, time, network, mqtt

SSID = "Tufts_Robot"
KEY = ""
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_TOPIC = "/movement"

# set up wifi connection
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('Connecting to Wi-Fi...')
        wlan.connect(SSID, KEY) 

        # wait until wifi is connected
        while not wlan.isconnected():
            time.sleep(1)
            print('Waiting for Wi-Fi connection...')
    print('Wi-Fi connected:', wlan.ifconfig())

# initialize the mqtt client
client = mqtt.MQTTClient("ME_35", MQTT_BROKER, port=MQTT_PORT)

# func to publish movement commands
def publish_command(command):
    client.publish(MQTT_TOPIC, command)
    print("Published command:", command)

# connect to mqtt broker
def connect_mqtt():
    connected = False
    while not connected:
        try:
            print('Attempting to connect to MQTT broker...')
            client.connect()
            print('Connected to MQTT broker')
            connected = True
        except OSError as e:
            print("Failed to connect to MQTT broker:", e)
            time.sleep(2)  # wait and retry

# initiaize camera
sensor.reset()
sensor.set_pixformat(sensor.RGB565)  
sensor.set_framesize(sensor.QVGA)   
sensor.skip_frames(time=2000)
sensor.set_auto_gain(False)
sensor.set_auto_whitebal(False)
clock = time.clock()

# connect to wifi
connect_wifi()

# connect to mqtt broker
connect_mqtt()

# AprilTag family
tag_families = image.TAG36H11

while True:
    clock.tick()
    img = sensor.snapshot()  # capture image
    for tag in img.find_apriltags(families=tag_families):  # detect AprilTags
        print("Tag ID:", tag.id)

        # send mqtt command based on tag
        if tag.id == 562:
            publish_command('forward')  
        elif tag.id == 563:
            publish_command('left')  
        elif tag.id == 564:
            publish_command('right')  
        elif tag.id == 565:
            publish_command('stop')  
        elif tag.id == 566:
            publish_command('reverse') 

    time.sleep(0.1)  # delay to avoid spamming

