# Reolink MQTT Bridge

A simple and lightweight Python web server that listens for incoming JSON webhooks from Reolink cameras and publishes them to an MQTT topic.

This is useful for integrating Reolink camera alerts with home automation or IoT systems that use MQTT.
Features

* Listens for POST requests on the /webhook endpoint.
* Validates that the request body is JSON and contains a specific key.
* Publishes the nested JSON object to a configurable MQTT topic.
* Uses Python's standard logging library for clean, timestamped output.
* Configurable via environment variables.
* Installation

You can install this application directly using pip. It's recommended to do this within a virtual environment.

### Clone the repository (or just download the files)
```
git clone https://github.com/yourusername/reolink-mqtt-bridge.git
cd reolink-mqtt-bridge
pip install -e .
```
Once installed, you can run the server using the command-line script created by setup.py.

```
reolink-bridge
```

## Configuration

The server can be configured using the following environment variables:

    FLASK_PORT: The port for the web server (default: 5000).

    MQTT_BROKER: The hostname or IP address of your MQTT broker (default: localhost).

    MQTT_PORT: The port for your MQTT broker (default: 1883).

    MQTT_TOPIC: The MQTT topic to publish messages to (default: home/alarms/camera).

Example:

export MQTT_BROKER="192.168.1.100"
export MQTT_TOPIC="reolink/alerts/person"
reolink-bridge

