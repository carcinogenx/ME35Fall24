import time
import uasyncio as asyncio 
from BLE_CEEO import Yell
from machine import ADC, Pin

# MIDI Commands
NoteOn = 0x90
NoteOff = 0x80
velocity = {'off': 0, 'f': 80}  # velocity settings

# light sensor setup
ldr_pin = ADC(Pin(27))
COVERED_THRESHOLD = 1000  

# Initialize BLE MIDI device
p = Yell('Pico-MIDI', verbose=True, type='midi')
p.connect_up()  # Connect to BLE MIDI device

# Define channel
channel = 0x0F & 0  # MIDI channel 0

# LED setup (GPIO 14, 15, 16, 17 for LEDs)
led_1 = Pin(14, Pin.OUT)
led_2 = Pin(15, Pin.OUT)
led_3 = Pin(16, Pin.OUT)
led_4 = Pin(17, Pin.OUT)

# Function to read light sensor and check if sensor is covered
def is_sensor_covered():
    ldr_value = ldr_pin.read_u16()
    voltage = (ldr_value / 65535) * 3.3
    print("LDR value:", ldr_value, "Voltage:", voltage)
    return ldr_value > COVERED_THRESHOLD

# Function to send MIDI Note On command
async def send_midi_note_on(note, led=None):
    try:
        timestamp_ms = time.ticks_ms()
        tsM = (timestamp_ms >> 7 & 0b111111) | 0x80
        tsL = 0x80 | (timestamp_ms & 0b1111111)
        payload = bytes([tsM, tsL, NoteOn | channel, note, velocity['f']])
        p.send(payload)
        print(f"Sent Note ON: {note}")
        if led:
            led.on()  # Turn on the LED when sending Note On
    except Exception as e:
        print(f"Error sending Note ON: {e}")

# Function to send MIDI Note Off command
async def send_midi_note_off(note, led=None):
    try:
        timestamp_ms = time.ticks_ms()
        tsM = (timestamp_ms >> 7 & 0b111111) | 0x80
        tsL = 0x80 | (timestamp_ms & 0b1111111)
        payload = bytes([tsM, tsL, NoteOff | channel, note, velocity['off']])
        p.send(payload)
        print(f"Sent Note OFF: {note}")
        if led:
            led.off()  # Turn off the LED when sending Note Off
    except Exception as e:
        print(f"Error sending Note OFF: {e}")

# Check for button presses and send MIDI notes with light sensor control
async def check_buttons_and_light_sensor():
    button_1 = Pin(0, Pin.IN, Pin.PULL_UP)
    button_2 = Pin(1, Pin.IN, Pin.PULL_UP)
    button_3 = Pin(2, Pin.IN, Pin.PULL_UP)
    button_4 = Pin(3, Pin.IN, Pin.PULL_UP)

    while True:
        try:
            if not is_sensor_covered():  # Sensor uncovered, proceed with notes
                if not button_1.value():
                    print("Button 1 pressed")
                    await send_midi_note_on(60, led_1)  # Send MIDI note (C4)
                    await asyncio.sleep(1)  # Duration for note being played
                    await send_midi_note_off(60, led_1)

                if not button_2.value():
                    print("Button 2 pressed")
                    await send_midi_note_on(62, led_2)  # Send MIDI note (D4)
                    await asyncio.sleep(1)
                    await send_midi_note_off(62, led_2)

                if not button_3.value():
                    print("Button 3 pressed")
                    await send_midi_note_on(64, led_3)  # Send MIDI note (E4)
                    await asyncio.sleep(1)
                    await send_midi_note_off(64, led_3)

                if not button_4.value():
                    print("Button 4 pressed")
                    await send_midi_note_on(65, led_4)  # Send MIDI note (F4)
                    await asyncio.sleep(1)
                    await send_midi_note_off(65, led_4)

            else:
                print("Sensor is covered, sending silent Note ON.")
                await send_midi_note_on(0)  # Send a no-noise note without LED control
                await asyncio.sleep(2)  # Wait longer when sensor is covered

            await asyncio.sleep(0.1)  # Small delay for CPU usage
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

