from pyscript.js_modules import teach, pose, ble_library, mqtt_library

async def run_model(URL2):
    s = teach.s  # or s = pose.s
    s.URL2 = URL2
    await s.init()

def get_predictions(num_classes):
    predictions = []
    for i in range (0,num_classes):
        divElement = document.getElementById('class' + str(i))
        if divElement:
            divValue = divElement.innerHTML
            predictions.append(divValue)
    return predictions

#initialize mqtt
mqtt_broker = 'broker.hivemq.com'
port = 1883
topic_sub = '/movement'      
client = mqtt_library.myClient
print('Connected to %s MQTT broker' % (mqtt_broker))
import asyncio
await run_model("https://teachablemachine.withgoogle.com/models/sPXnSlGg8/") # model link
topic_pub = '/movement'

while True:
    predictions = get_predictions(2)
    values = [float(item.split(': ')[1]) for item in predictions]
    print(values)
    if values[0] >= 0.90:
        client.publish("/movement", "run")
    elif values[1] >= 0.90:
        client.publish("/movement", "stop")
