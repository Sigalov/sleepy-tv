import argparse
import asyncio
from aioswitcher.api import Command, SwitcherType1Api

async def control_device(action, device_id, device_key, ip_address, timer=None):
    async with SwitcherType1Api(ip_address, device_id, device_key) as api:
        if action == "turn_off":
            await api.control_device(Command.OFF)
        elif action == "turn_on":
            if timer:
                await api.control_device(Command.ON, timer)
            else:
                await api.control_device(Command.ON, 15)  # Default to 15 minutes if no timer is provided
        print(f"Device {action} command sent to {device_id} at {ip_address}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Control a Switcher device")
    parser.add_argument("action", choices=["turn_on", "turn_off"], help="Action to perform on the device")
    parser.add_argument("-d", "--device-id", required=True, help="The identification of the device")
    parser.add_argument("-l", "--device-key", required=True, help="The login key of the device")
    parser.add_argument("-i", "--ip-address", required=True, help="The IP address assigned to the device")
    parser.add_argument("-t", "--timer", type=int, help="Set minutes timer for turn on operation")

    args = parser.parse_args()

    asyncio.run(control_device(args.action, args.device_id, args.device_key, args.ip_address, args.timer))
