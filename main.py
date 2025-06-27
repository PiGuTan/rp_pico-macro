import board

import usb_hid
import digitalio
import time
from adafruit_hid.keycode import Keycode
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.mouse import Mouse
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode

import asyncio
from switch import Switch,switches


async def main():
    while True:
        for switch in switches:
            if not switch.button.value and not switch.running:  # Button is pressed
                asyncio.create_task(switch.action())
                await asyncio.sleep(0.01)
            
        await asyncio.sleep(0.01) # Small delay to reduce CPU usage

try:
    asyncio.run(main())
except KeyboardInterupt:
    pass
