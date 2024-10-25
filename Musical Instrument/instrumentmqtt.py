import time
import uasyncio as asyncio
from BLE_CEEO import Yell
from machine import ADC, Pin
from mqtt import MQTTClient

# MQTT settings
MQTT_BROKER = "broker.hivemq.com"
MQTT_CONTROL_TOPIC = "/instrument/control"
MQTT_KEY_CHANGE_TOPIC = "/key_change"
MQTT_VOLUME_TOPIC = "/instrument/volume"
instrument_active = False
current_key = "C Major"
current_volume = 80  

# MIDI 
NoteOn = 0x90
NoteOff = 0x80
velocity = {'off': 0}  # Velocity off is always 0

# Light sensor setup
ldr_pin = ADC(Pin(27))
COVERED_THRESHOLD = 1200

# Initialize BLE MIDI 
p = Yell('Pico-MID', verbose=True, type='midi')
p.connect_up()

# Define channel
channel = 0x0F & 0

# LED setup (GPIO 14, 15, 16, 17 for LEDs)
led_1 = Pin(14, Pin.OUT)
led_2 = Pin(15, Pin.OUT)
led_3 = Pin(16, Pin.OUT)
led_4 = Pin(17, Pin.OUT)

# MQTT message handling 
def mqtt_callback(topic, msg):
    global instrument_active, current_key, current_volume
    if topic == MQTT_CONTROL_TOPIC:
        if msg == b"on":
            instrument_active = True
        elif msg == b"off":
            instrument_active = False
    elif topic == MQTT_KEY_CHANGE_TOPIC:
        current_key = msg.decode()
        print(f"Current key set to: {current_key}")
    elif topic == MQTT_VOLUME_TOPIC:
        current_volume = int(msg.decode())  # Update volume from Dahal board
        print(f"Current volume set to: {current_volume}")

# Initialize MQTT Client and connect
client = MQTTClient("PicoInstrument", MQTT_BROKER)
client.set_callback(mqtt_callback)
client.connect()
client.subscribe(MQTT_CONTROL_TOPIC)
client.subscribe(MQTT_KEY_CHANGE_TOPIC)
client.subscribe(MQTT_VOLUME_TOPIC)

# Function to read light sensor and check if sensor is covered
def is_sensor_covered():
    ldr_value = ldr_pin.read_u16()
    voltage = (ldr_value / 65535) * 3.3
    print("LDR value:", ldr_value, "Voltage:", voltage)
    return ldr_value > COVERED_THRESHOLD

# Function to send MIDI Note On command with adjustable volume
async def send_midi_note_on(note, led=None):
    if instrument_active:
        try:
            timestamp_ms = time.ticks_ms()
            tsM = (timestamp_ms >> 7 & 0b111111) | 0x80
            tsL = 0x80 | (timestamp_ms & 0b1111111)
            payload = bytes([tsM, tsL, NoteOn | channel, note, current_volume])
            p.send(payload)
            print(f"Sent Note ON: {note} with volume {current_volume}")
            if led:
                led.on()
        except Exception as e:
            print(f"Error sending Note ON: {e}")

# Function to send MIDI Note Off command
async def send_midi_note_off(note, led=None):
    if instrument_active:
        try:
            timestamp_ms = time.ticks_ms()
            tsM = (timestamp_ms >> 7 & 0b111111) | 0x80
            tsL = 0x80 | (timestamp_ms & 0b1111111)
            payload = bytes([tsM, tsL, NoteOff | channel, note, velocity['off']])
            p.send(payload)
            print(f"Sent Note OFF: {note}")
            if led:
                led.off()
        except Exception as e:
            print(f"Error sending Note OFF: {e}")

# Function to play notes based on current key
async def play_note_for_key(note, led=None):
    if current_key == "C Major":
        await send_midi_note_on(note, led)
    elif current_key == "G Major":
        await send_midi_note_on(note + 7, led)  

# Check for button presses and send MIDI notes with light sensor control
async def check_buttons_and_light_sensor():
    button_1 = Pin(0, Pin.IN, Pin.PULL_UP)
    button_2 = Pin(1, Pin.IN, Pin.PULL_UP)
    button_3 = Pin(2, Pin.IN, Pin.PULL_UP)
    button_4 = Pin(3, Pin.IN, Pin.PULL_UP)

    while True:
        try:
            client.check_msg()  # Check for new MQTT messages

            if instrument_active and not is_sensor_covered():
                if not button_1.value():
                    print("Button 1 pressed")
                    await play_note_for_key(60, led_1)
                    await asyncio.sleep(1)
                    await send_midi_note_off(60, led_1)

                if not button_2.value():
                    print("Button 2 pressed")
                    await play_note_for_key(62, led_2)
                    await asyncio.sleep(1)
                    await send_midi_note_off(62, led_2)

                if not button_3.value():
                    print("Button 3 pressed")
                    await play_note_for_key(64, led_3)
                    await asyncio.sleep(1)
                    await send_midi_note_off(64, led_3)

                if not button_4.value():
                    print("Button 4 pressed")
                    await play_note_for_key(65, led_4)
                    await asyncio.sleep(1)
                    await send_midi_note_off(65, led_4)

            await asyncio.sleep(0.1)
        except Exception as e:
            print(f"Error in button checking loop: {e}")

# Main function using asyncio
async def main():
    try:
        print("Starting MIDI note playback with button and sensor control.")
        await check_buttons_and_light_sensor()
    finally:
        print("BLE MIDI playback running indefinitely.")

# Run the main function
asyncio.run(main())
