import network
import time

def WifiConnectHome():
    
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect('28Belknap2', 'Pisinski12!')

    while wlan.ifconfig()[0] == '0.0.0.0':
        print('.', end=' ')
        time.sleep(1)

# We should have a valid IP now via DHCP
    print(wlan.ifconfig())

