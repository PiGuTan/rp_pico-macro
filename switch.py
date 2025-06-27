import board
import asyncio
import json
import usb_hid
import digitalio
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

abort = False # TODO: make this controllable

class Switch:
    def __init__(self,button_no:int,led_no:int=-1):
        self.button_no: int = button_no
        self.pin = pin_map[button_no]
        self.sequence:list[int] = config_data[button_no]["sequence"]
        self.delay:float = config_data[button_no]["delay"]/1000
        self.running = False

        self.button = digitalio.DigitalInOut(self.pin)
        self.button.direction = digitalio.Direction.INPUT
        self.button.pull = digitalio.Pull.UP
        

        self.led = None # TODO: create for led
        
    async def action(self) -> bool:
        if self.running:
            return False
        print("s",self.button_no, sep="", end=" ")
        # TODO: led on
        for sequence in self.sequence:
            self.running = True
            if abort:
                break
            split = sequence.split(".")
            if split[0] == "Keycode":
                keyboard.send(action_map[split[0]][split[1]])
            elif split[0] == "Mouse":
                mouse.click(action_map[split[0]][split[1]])
            await asyncio.sleep(self.delay)
        print("e",self.button_no, sep="", end=" ")
        # TODO: led_off
        self.running = False
        return not abort


switches: Switch = []
for pin_key in config_data.keys():
    switches.append(Switch(pin_key))


    
    