# Code to run for Teachable Machine Key Change
from pyscript.js_modules import teach, mqtt_library

# Set up MQTT connection
myClient = mqtt_library.myClient("broker.hivemq.com", 8884)
mqtt_connected = False
sub_topic = 'ME35-24/listen'
pub_topic = 'ME35-24/key_change'

async def received_mqtt_msg(message):
    message = myClient.read().split('\t')  # Handle received messages if needed

# Function to initialize and run the Teachable Machine model
async def run_model(URL2):
    s = teach.s
    s.URL2 = URL2
    await s.init()

# Function to connect to MQTT broker and subscribe to necessary topics
async def connect(name):
    global mqtt_connected
    myClient.init()
    while not myClient.connected:
        await asyncio.sleep(2)
    myClient.subscribe(sub_topic)
    myClient.callback = received_mqtt_msg
    mqtt_connected = True

async def disconnect():
    print('disconnected')

# Publish MQTT messages for key changes
def send(message):
    print('sending ', message)
    myClient.publish(pub_topic, message)

# Get model predictions and return
def get_predictions(num_classes):
    predictions = []
    for i in range(num_classes):
        divElement = document.getElementById('class' + str(i))
        if divElement:
            divValue = divElement.innerHTML
            predictions.append(divValue)
    return predictions

# Initialize and run the Teachable Machine model and MQTT connection
import asyncio
await run_model("https://teachablemachine.withgoogle.com/models/rNj5zR8_P/")  
await connect('KeyChanger')

# Continuously send key changes based on model predictions
while True:
    if mqtt_connected:
        predictions = get_predictions(2) 
        if predictions[0] == "C Major":
            send("C Major")
        elif predictions[1] == "G Major":
            send("G Major")
    await asyncio.sleep(2)
