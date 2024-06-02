import asyncio
import json
import os
from dataclasses import asdict
from aioswitcher.bridge import SwitcherBridge

class DeviceScanner:
    def __init__(self, filename="device_details.json"):
        self.device_ip = None
        self.device_id = None
        self.device_key = None
        self.device_found = False
        self.filename = filename

    def on_device_found_callback(self, device):
        if not self.device_found:
            device_dict = asdict(device)
            if device_dict['device_type'].name == "POWER_PLUG":
                self.device_ip = device_dict['ip_address']
                self.device_id = device_dict['device_id']
                self.device_key = device_dict['device_key']
                self.device_found = True
                print(f"Found device: IP={self.device_ip}, ID={self.device_id}, DEVICE_KEY={self.device_key}")
                self.save_device_details()

    async def scan_devices(self):
        async with SwitcherBridge(self.on_device_found_callback):
            while not self.device_found:
                await asyncio.sleep(1)

    def save_device_details(self):
        data = {
            "device_ip": self.device_ip,
            "device_id": self.device_id,
            "device_key": self.device_key
        }
        with open(self.filename, 'w') as f:
            json.dump(data, f)
        print(f"Device details saved to {self.filename}")

    def load_device_details(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as f:
                data = json.load(f)
                self.device_ip = data.get("device_ip")
                self.device_id = data.get("device_id")
                self.device_key = data.get("device_key")
                self.device_found = True
                print(f"Loaded device details from {self.filename}")
        else:
            print(f"No existing device details found, scanning for devices...")

    def get_device_info(self):
        return self.device_ip, self.device_id, self.device_key
