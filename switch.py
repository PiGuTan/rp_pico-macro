import board
import asyncio
import json
import usb_hid
import digitalio
import os

from adafruit_hid.keycode import Keycode
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.mouse import Mouse
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode

from mapping import pin_map, action_map

cc = ConsumerControl(usb_hid.devices)
keyboard = Keyboard(usb_hid.devices)
mouse = Mouse(usb_hid.devices)
write_text = KeyboardLayoutUS(keyboard)

try:
    with open('config.json', 'r') as f:
        config_data = json.load(f)
except OSError as e:
    print("Error opening or reading file:", e)
except KeyError as e:
    print("Missing key in JSON data:", e)

class Switch:
    abort_button = None
    def __init__(self,button_no:int):
        self.button_no: int = button_no
        self.pin = pin_map[button_no]
        
        self.delay:int = 1000
        if "delay" in config_data[button_no]:
            self.delay = config_data[button_no]["delay"]
        
        self.button = digitalio.DigitalInOut(self.pin)
        self.button.direction = digitalio.Direction.INPUT
        self.button.pull = digitalio.Pull.UP
        self.running = False
        
    async def action(self) -> bool:
        print("n",self.button_no, sep="", end=" ")
        pass

class Action_switch(Switch):
    def __init__(self,button_no:int):
        super().__init__(button_no)
        self.sequence:list[int] = config_data[button_no]["sequence"]
        
        # led config
        if "led" in config_data[button_no]:
            self.led_no:int = config_data[button_no]["led"]
            self.led_pin = pin_map[self.led_no]
            self.led = digitalio.DigitalInOut(self.led_pin)
            self.led.direction = digitalio.Direction.OUTPUT
        else:
            self.led = None
            self.led_pin = None
            self.led_no = -1
    
    async def action(self) -> bool:
        if self.running:
            return False
        print("s",self.button_no, sep="", end=" ")
        if self.led:
            self.led.value = True
        self.running=True
        
        for sequence in self.sequence:
            abort = not Switch.abort_button.value
            if abort:
                break
            split = sequence.split(".")
            if debug:
                try:
                    print(action_map[split[0]][split[1]],end=" ")
                except KeyError:
                    print("?",split,sep="")
            else:
                if split[0] == "Keycode":
                    keyboard.send(action_map[split[0]][split[1]])
                elif split[0] == "Mouse":
                    mouse.click(action_map[split[0]][split[1]])
            if self.led:
                self.led.value = True
            await asyncio.sleep_ms(self.delay)
            if self.led:
                self.led.value = False
        self.running = False

        print("a" if abort else "e",self.button_no, sep="", end=" ")
        return not abort

class Value_switch(Switch):
    """
    switch that detects values
    
    """
    def __init__(self,button_no:int):
        super().__init__(button_no)
        self.action_config:str = config_data[button_no]["action"]
        if self.action_config == "abort":
            Switch.abort_button = self.button
        
debug:bool = bool(os.getenv("DEBUG"))
switches: Switch = []
for pin_key in config_data.keys():
    if "action" in config_data[pin_key]:
        try:
            Value_switch(pin_key)
            print("Successfully configured pin -", pin_key)
        except Exception as e:
            print("Failed to config pin -", pin_key, "-", e)
    else:
        try:
            switches.append(Action_switch(pin_key))
            print("Successfully configured pin -", pin_key)
        except Exception as e:
            print("Failed to config pin -", pin_key, "-", e)


    
    