from flask import Flask, render_template, redirect, url_for, request
import threading
import asyncio
from main import main as sleepy_tv_main, service_running_flag
from socket_control.device_scanner import DeviceScanner

app = Flask(__name__)
service_running = False
service_thread = None

def run_service(eye_ar_thresh, eye_ar_consec_frames):
    global service_running
    service_running_flag.set()
    asyncio.run(sleepy_tv_main(eye_ar_thresh, eye_ar_consec_frames))
    service_running = False

@app.route('/')
def index():
    global service_running
    status = "Running" if service_running else "Not Running"
    scanner = DeviceScanner()
    scanner.load_device_details()
    device_info = {
        "device_ip": scanner.device_ip,
        "device_id": scanner.device_id,
        "device_key": scanner.device_key
    }
    return render_template('index.html', status=status, device_info=device_info)

@app.route('/start', methods=['POST'])
def start_service():
    global service_running, service_thread
    if not service_running:
        eye_ar_thresh = float(request.form['eye_ar_thresh'])
        eye_ar_consec_frames = int(request.form['eye_ar_consec_frames'])
        service_thread = threading.Thread(target=run_service, args=(eye_ar_thresh, eye_ar_consec_frames))
        service_thread.start()
        service_running = True
    return redirect(url_for('index'))

@app.route('/stop', methods=['POST'])
def stop_service():
    global service_running, service_thread
    if service_running:
        service_running_flag.clear()
        if service_thread:
            service_thread.join()  # Wait for the thread to finish
            service_thread = None
        service_running = False
    return redirect(url_for('index'))

@app.route('/restart_scan', methods=['POST'])
def restart_scan():
    scanner = DeviceScanner()
    asyncio.run(scanner.scan_devices())
    scanner.save_device_details()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
