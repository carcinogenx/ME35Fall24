import time
from mqtt import MQTTClient
from neopixel import NeoPixel
from machine import Pin, PWM
import random
import WifiConnect  # connect to wifi


class Nightlight:
    #constructor method to initalize attributes
    def __init__(self, button_pin, buzzer_pin, blue_led_pin, neopixel_pin):
        # set up button, LED, and buzzer
        self.button = Pin(button_pin, Pin.IN, Pin.PULL_UP)  # Button with pull-up resistor
        self.buzzer = Pin(buzzer_pin, Pin.OUT)
        self.blue_led = PWM(Pin(blue_led_pin))
        self.blue_led.freq(1000)
        
        # set up neopixel
        self.np = NeoPixel(Pin(neopixel_pin), 1)
        
        # set up nightlight states
        self.nightlight_on = False
        self.breathe_state = 0  # Track the current state of the breathing LED
        self.breathe_direction = 1  # 1 for increasing brightness, -1 for decreasing brightness
        self.last_breathe_time = time.ticks_ms()  # Track the last time we updated the LED brightness
        self.breathe_interval = 10  # Adjust the interval for smoother breathing (in ms)

    #method to create the breathe effect while not blocking button push inputs
    def breathe_led_non_blocking(self):
        # non-blocking breathe LED effect
        current_time = time.ticks_ms()
        if time.ticks_diff(current_time, self.last_breathe_time) > self.breathe_interval:
            self.last_breathe_time = current_time

            # update the LED brightness based on breathe state
            self.blue_led.duty_u16(self.breathe_state)
            self.breathe_state += self.breathe_direction * 10  # change brightness

            # reverse direction at max and mini
            if self.breathe_state >= 1024:
                self.breathe_state = 1024
                self.breathe_direction = -1
            elif self.breathe_state <= 0:
                self.breathe_state = 0
                self.breathe_direction = 1
    
    #method to turn off LED
    def turn_off_breathing_led(self):
        # completely turn off the breathing LED by setting duty cycle to 0
        print("Turning off breathing LED")
        self.blue_led.duty_u16(0)
    
    #method to change color of neopixel
    def change_neopixel(self):
        # choose random values for RGB
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        #set neopixel to that color
        self.np[0] = (r, g, b)
        self.np.write()

    #method to turn off neopixel
    def turn_off_neopixel(self):
        print("Turning off Neopixel")
        self.np[0] = (0, 0, 0)
        self.np.write()

    #method to beep buzzer for short duration
    def beep_buzzer(self):
        self.buzzer.freq(freq)
        self.buzzer.duty_u16(512)

    #method to check if the button is in pressed position (0 when pressed with PULL_UP)
    def check_button(self):
        if self.button.value() == 0:
            print("Button pressed!")  # debugging statement
            self.change_neopixel() # trigger color change
            self.beep_buzzer(440) #beep button
            #delay to prevent multiple actions on a single press
            time.sleep(0.5)
            self.buzzer.duty_u16(0)

    #method for mqtt start and stop
    def handle_mqtt(self, message):
        msg = message.decode("utf-8")
        print(f"Received MQTT message: {msg}")  # debugging statement
        if msg == "start": #start on start
            print("Starting nightlight...")  # debugging statement
            self.nightlight_on = True
        elif msg == "stop": #stop on stop and turn off LEDs
            print("Stopping nightlight...")  # debugging statement
            self.nightlight_on = False
            # Turn off Neopixel and breathing LED when stopping the nightlight
            self.turn_off_neopixel()
            self.turn_off_breathing_led()
        else:
            print(f"Unrecognized message: {msg}")

def main():
    # WifiConnect is automatically run when imported
    print("Checking Wi-Fi connection...")
    time.sleep(3)  # Wait a few seconds to ensure the connection is complete

    # initialize the nightlight class
    nightlight = Nightlight(button_pin=20, buzzer_pin=18, blue_led_pin=0, neopixel_pin=28) #connect correct pins
    # define the mqtt callback function within main() so it can access 'nightlight'
    def on_message(topic, msg):
        print(f"Message received on topic: {topic.decode('utf-8')}")  # debugging statement
        print(f"Payload: {msg.decode('utf-8')}")  # debugging statement
        print("Passing message to handle_mqtt")
        nightlight.handle_mqtt(msg)

    # set up mqtt client
    client = MQTTClient("pico_nightlight", "broker.hivemq.com")

    if client is None:
        print("Failed to create MQTT client")
        return  # exit the function if the client creation fails

    client.set_callback(on_message)

    try:
        client.connect()
        print("Connected to MQTT broker")
        client.subscribe("nightlight/control")
        print("Subscribed to topic: nightlight/control")
    except OSError as e:
        print(f"Failed to connect to MQTT broker: {e}")
        return  # exit if failed to connect

    try:
        while True:
            # Check for new MQTT messages
            client.check_msg()

            if nightlight.nightlight_on:
                # breathe LED effect
                nightlight.breathe_led_non_blocking()

            # check if the button is pressed
            nightlight.check_button()

            time.sleep(0.01)  # small delay to avoid flooding

    except KeyboardInterrupt:
        print("Nightlight stopped.")
    finally:
        # Disconnect from MQTT broker on exit
        client.disconnect()

if __name__ == "__main__":
    main()
