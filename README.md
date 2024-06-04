
# SleepyTV

SleepyTV is a project designed to automatically turn off your TV when you fall asleep. It uses a web camera to detect when your eyes are closed for a certain duration and then turns off the TV using a smart socket connected to a Raspberry Pi.

## Features

- Detects if eyes are closed for a specified duration using a web camera
- Turns off the TV using a smart socket
- Runs on a Raspberry Pi
- Dockerized for easy deployment
- Auto-start on boot
- Remote access via SSH and ngrok

## Installation

1. Clone the repository:
    ```bash
    git clone <repository-url>
    cd SleepyTV
    ```

2. Build and run the Docker container:
    ```bash
    docker-compose up --build
    ```

3. Set up auto-launch on boot (see instructions below).

## Usage

To control the smart socket, use the following commands:

```bash
python switcher/control_device.py turn_off -d DEVICE_ID -l DEVICE_KEY -i IP_ADDRESS
python switcher/control_device.py turn_on -d DEVICE_ID -l DEVICE_KEY -i IP_ADDRESS
```

## Configuration

### Web Interface

The SleepyTV project includes a web interface for configuring and controlling the service. The interface allows you to set the Eye Aspect Ratio (EAR) threshold, the number of consecutive frames required to detect a blink, and the frames per second (FPS) for the camera.

### Start the Service

1. Open the web interface in your browser (replace `localhost` with your Raspberry Pi's IP address if accessing remotely):
    ```url
    http://localhost:5001
    ```

2. Set the desired values for:
    - Eye Aspect Ratio Threshold
    - Consecutive Frames for Blink Detection
    - Frames Per Second (FPS)

3. Click the "Start Service" button to start the eye monitoring service.

### Stop the Service

To stop the service, click the "Stop Service" button on the web interface.

### Restart Device Scan

If you need to rescan for the smart socket device, click the "Restart Device Scan" button on the web interface.

## Code Overview

### `flask_app.py`

This is the main Flask application that serves the web interface. It includes routes for starting and stopping the service, as well as rescanning for devices.

### `main.py`

This is the main entry point for the eye monitoring service. It initializes the `EyeMonitor` class with the specified parameters and starts the monitoring loop.

### `EyeMonitor` Class

The `EyeMonitor` class uses OpenCV and dlib to detect faces and monitor eye aspect ratios. It triggers the TV turn-off command when the eyes are detected as closed for a specified duration.

### HTML Template

The `index.html` file is the web interface for controlling the service. It includes form fields for setting the EAR threshold, consecutive frames, and FPS, and displays the current status of the service and connected device information.

## Auto-Launch on Boot

To set up SleepyTV to auto-launch on boot, follow these steps:

1. Create a systemd service file (e.g., `sleepytv.service`):
    ```ini
    [Unit]
    Description=SleepyTV Service
    After=network.target

    [Service]
    ExecStart=/usr/bin/docker-compose -f /path/to/your/docker-compose.yml up
    WorkingDirectory=/path/to/your/project
    Restart=always
    User=pi

    [Install]
    WantedBy=multi-user.target
    ```

2. Enable the service:
    ```bash
    sudo systemctl enable sleepytv.service
    sudo systemctl start sleepytv.service
    ```

## Remote Access

For remote access, you can use SSH and ngrok to securely expose your local server to the internet.

### SSH

Enable SSH on your Raspberry Pi and connect using:
```bash
ssh pi@your-pi-ip
```

### ngrok

Set up ngrok to expose the Flask web interface:
```bash
ngrok http 5001
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.
