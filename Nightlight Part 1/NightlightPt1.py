import time
from mqtt import MQTTClient
from neopixel import NeoPixel
from machine import Pin, PWM
import random
import WifiConnectHome  # connect to wifi


class Nightlight:
    def __init__(self, button_pin, buzzer_pin, blue_led_pin, neopixel_pin):
        # Set up button, LED, and buzzer
        self.button = Pin(button_pin, Pin.IN, Pin.PULL_UP)  # Button with pull-up resistor
        self.buzzer = Pin(buzzer_pin, Pin.OUT)
        self.blue_led = PWM(Pin(blue_led_pin))
        self.blue_led.freq(1000)
        
        # Neopixel set up
        self.np = NeoPixel(Pin(neopixel_pin), 1)
        
        # Nightlight state
        self.nightlight_on = False
        self.breathe_state = 0  # Track the current state of the breathing LED
        self.breathe_direction = 1  # 1 for increasing brightness, -1 for decreasing brightness
        self.last_breathe_time = time.ticks_ms()  # Track the last time we updated the LED brightness
        self.breathe_interval = 10  # Adjust the interval for smoother breathing (in ms)

    def breathe_led_non_blocking(self):
        # Non-blocking breathe LED effect
        current_time = time.ticks_ms()
        if time.ticks_diff(current_time, self.last_breathe_time) > self.breathe_interval:
            self.last_breathe_time = current_time

            # Update the LED brightness based on the current breathe state
            self.blue_led.duty_u16(self.breathe_state)
            self.breathe_state += self.breathe_direction * 10  # Change brightness step by step

            # Reverse direction at maximum and minimum brightness
            if self.breathe_state >= 1024:
                self.breathe_state = 1024
                self.breathe_direction = -1
            elif self.breathe_state <= 0:
                self.breathe_state = 0
                self.breathe_direction = 1

    def turn_off_breathing_led(self):
        # Completely turn off the breathing LED by setting duty cycle to 0
        print("Turning off breathing LED")
        self.blue_led.duty_u16(0)

    def change_neopixel(self):
        # Change the color of the Neopixel to a random color
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        self.np[0] = (r, g, b)
        self.np.write()

    def turn_off_neopixel(self):
        # Turn off the Neopixel by setting it to (0, 0, 0)
        print("Turning off Neopixel")
        self.np[0] = (0, 0, 0)
        self.np.write()

    def beep_buzzer(self):
        # Beep the buzzer for a short duration
        self.buzzer.value(1)
        time.sleep(0.1)
        self.buzzer.value(0)

    def check_button(self):
        # Check if the button is pressed (button value is 0 when pressed with PULL_UP)
        if self.button.value() == 0:
            print("Button pressed!")  # Debugging statement
            self.change_neopixel()
            self.beep_buzzer()
            # Simple delay to prevent multiple actions on a single press
            time.sleep(0.5)

    def handle_mqtt(self, message):
        # Handle MQTT start and stop commands
        msg = message.decode("utf-8")
        print(f"Received MQTT message: {msg}")  # Debugging statement
        if msg == "start":
            print("Starting nightlight...")  # Debugging statement
            self.nightlight_on = True
        elif msg == "stop":
            print("Stopping nightlight...")  # Debugging statement
            self.nightlight_on = False
            # Turn off Neopixel and breathing LED when stopping the nightlight
            self.turn_off_neopixel()
            self.turn_off_breathing_led()
        else:
            print(f"Unrecognized message: {msg}")

def main():
    # WifiConnectHome is automatically run when imported
    print("Checking Wi-Fi connection...")
    time.sleep(3)  # Wait a few seconds to ensure the connection is complete

    # Initialize the nightlight class
    nightlight = Nightlight(button_pin=20, buzzer_pin=18, blue_led_pin=0, neopixel_pin=28)  # Using GPIO 20 for the built-in button

    # Define the MQTT callback function within main() so it can access 'nightlight'
    def on_message(topic, msg):
        print(f"Message received on topic: {topic.decode('utf-8')}")  # Debugging statement
        print(f"Payload: {msg.decode('utf-8')}")  # Debugging statement
        print("Passing message to handle_mqtt")
        nightlight.handle_mqtt(msg)

    # Setup MQTT client
    client = MQTTClient("pico_nightlight", "broker.hivemq.com")
    
    if client is None:
        print("Failed to create MQTT client")
        return  # Exit the function if the client creation fails

    client.set_callback(on_message)

    try:
        client.connect()
        print("Connected to MQTT broker")
        client.subscribe("nightlight/control")
        print("Subscribed to topic: nightlight/control")
    except OSError as e:
        print(f"Failed to connect to MQTT broker: {e}")
        return  # Exit if failed to connect

    try:
        while True:
            # Check for new MQTT messages
            client.check_msg()

            if nightlight.nightlight_on:
                # Non-blocking breathe LED effect
                nightlight.breathe_led_non_blocking()

            # Check if the button is pressed (simple press detection without debouncing)
            nightlight.check_button()

            time.sleep(0.01)  # Small delay to avoid flooding the CPU

    except KeyboardInterrupt:
        print("Nightlight stopped.")
    finally:
        # Disconnect from MQTT broker on exit
        client.disconnect()

if __name__ == "__main__":
    main()
