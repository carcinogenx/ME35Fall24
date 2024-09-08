import time
from machine import Pin

# set up the built-in button (pin 20) 
button = Pin(20, Pin.IN, Pin.PULL_UP)

# loop to check button state
while True:
    if button.value() == 0:
        print("Button pressed!")  # prints when button registers as pressed
    else:
        print("Button not pressed")  # prints when button registers as not pressed
    time.sleep(0.2)  # small delay to avoid flooding response
