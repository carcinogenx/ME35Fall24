import sensor, image, time, network, mqtt

SSID = "Tufts_Robot"
KEY = ""
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_TOPIC = "/movement"

# Setup Wi-Fi connection without a password
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('Connecting to Wi-Fi...')
        wlan.connect(SSID, KEY)  # No password needed

        # Add a loop to wait until the Wi-Fi is fully connected
        while not wlan.isconnected():
            time.sleep(1)
            print('Waiting for Wi-Fi connection...')
    print('Wi-Fi connected:', wlan.ifconfig())

# Initialize the MQTT client
client = mqtt.MQTTClient("ME_35", MQTT_BROKER, port=MQTT_PORT)

# Function to publish movement commands
def publish_command(command):
    client.publish(MQTT_TOPIC, command)
    print("Published command:", command)

# Connect to MQTT Broker with retries
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
            time.sleep(2)  # Wait and retry after 2 seconds

# Initialize camera
sensor.reset()
sensor.set_pixformat(sensor.RGB565)  # or grayscale
sensor.set_framesize(sensor.QVGA)    # QVGA is faster for image processing
sensor.skip_frames(time=2000)
sensor.set_auto_gain(False)
sensor.set_auto_whitebal(False)
clock = time.clock()

# Connect to Wi-Fi
connect_wifi()

# Connect to the MQTT Broker
connect_mqtt()

# AprilTag family
tag_families = image.TAG36H11

while True:
    clock.tick()
    img = sensor.snapshot()  # Capture image
    for tag in img.find_apriltags(families=tag_families):  # Detect AprilTags
        print("Tag ID:", tag.id)

        # Send MQTT command based on detected tag
        if tag.id == 562:
            publish_command('forward')  # Forward
        elif tag.id == 563:
            publish_command('left')  # Left
        elif tag.id == 564:
            publish_command('right')  # Right
        elif tag.id == 565:
            publish_command('stop')  # Stop
        elif tag.id == 566:
            publish_command('reverse')  # Backward

    time.sleep(0.1)  # Short delay to avoid spamming the broker

