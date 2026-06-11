import asyncio
from switch import Value_switch,Action_switch,switches

async def main():
    while True:
        for switch in switches:
            if not switch.button.value and not switch.running:
                # print(switch.action)
                asyncio.create_task(switch.action())
                await asyncio.sleep_ms(10)
            if switch.abort:
                continue
        await asyncio.sleep_ms(10) # Small delay to reduce CPU usage

try:
    asyncio.run(main())
except KeyboardInterrupt:
    pass
