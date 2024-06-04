import asyncio
import threading
from camera.eye_monitor import EyeMonitor
from socket_control.device_scanner import DeviceScanner

service_running_flag = threading.Event()


async def main(eye_ar_thresh, eye_ar_consec_frames, fps):
    scanner = DeviceScanner()
    scanner.load_device_details()  # Check if device details exist locally
    if not scanner.device_found:
        await scanner.scan_devices()  # Scan and save if not found locally
    device_ip, device_id, device_key = scanner.get_device_info()
    if device_ip and device_id and device_key:
        monitor = EyeMonitor(device_id, device_key, device_ip, service_running_flag, eye_ar_thresh,
                             eye_ar_consec_frames, fps)

        print(f"Starting EyeMonitor with eye_ar_thresh: {eye_ar_thresh}, eye_ar_consec_frames: {eye_ar_consec_frames}, fps: {fps}")

        monitor.monitor_eyes()
    else:
        print("No power plug device found.")


if __name__ == "__main__":
    service_running_flag.set()
    asyncio.run(main(0.25, 30, 30))
