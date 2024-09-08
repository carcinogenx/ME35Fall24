import time
from machine import Pin

# Set up the built-in button on GPIO 20 with pull-down resistor
button = Pin(20, Pin.IN, Pin.PULL_UP)

# Simple loop to check the button state
while True:
    if button.value() == 0:
        print("Button pressed!")  # This will print whenever the button is pressed
    else:
        print("Button not pressed")  # This will print when the button is not pressed
    time.sleep(0.2)  # Add a small delay to avoid flooding the output
