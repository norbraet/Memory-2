"""
GPIO Layout:

GND -> Pin 9
R -> Pin 11 (BCM 17)
G -> Pin 13 (BCM 27)
B -> Pin 15 (BCM 22)
"""

from gpiozero import PWMOutputDevice
from time import sleep

# Set up GPIO pins for Red, Green, and Blue channels
red = PWMOutputDevice(17)    # Red pin connected to GPIO 17
green = PWMOutputDevice(27)  # Green pin connected to GPIO 27
blue = PWMOutputDevice(22)   # Blue pin connected to GPIO 22

# Set the brightness of the RGB LED (0 to 1)
def set_color(r, g, b):
    red.value = r  # Set the brightness for Red
    green.value = g  # Set the brightness for Green
    blue.value = b  # Set the brightness for Blue

# Main loop to change colors
try:
    while True:
        # Red
        set_color(1, 0, 0)  # Full red

        # Green
        set_color(0, 1, 0)  # Full green
        sleep(1)
        
        # Blue
        set_color(0, 0, 0.5)  # Full blue
        sleep(1)
               
        # Yellow (Red + Green)
        set_color(1, 1, 0)  # Full red + green = yellow
        sleep(1)
        
        # Cyan (Green + Blue)
        set_color(0, 1, 1)  # Full green + blue = cyan
        sleep(1)
        
        # Magenta (Red + Blue)
        set_color(1, 0, 1)  # Full red + blue = magenta
        sleep(1)
        
        # White (All colors)
        set_color(1, 1, 1)  # Full red + green + blue = white
        sleep(1)
        
        # Off (No color)
        set_color(0, 0, 0)  # No color (turn off)
        sleep(1) 
        
        
except KeyboardInterrupt:
    print("Program stopped")
