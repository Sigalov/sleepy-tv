# SleepyTV

SleepyTV is a project designed to automatically turn off your TV when you fall asleep. It uses a web camera to detect when your eyes are closed for a certain duration and then turns off the TV using a smart socket connected to a Raspberry Pi.

## Features

- Detects if eyes are closed for 10 seconds using a web camera
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
