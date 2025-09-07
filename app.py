import os
import json
import logging
import argparse
from flask import Flask, request, jsonify
import paho.mqtt.client as mqtt

# --- Global variables that will be set in main() ---
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "home/alarms/camera"
MQTT_USER = None
MQTT_PASSWORD = None
FLASK_PORT = 5000

# --- Set up MQTT Client ---
def on_connect(client, userdata, flags, rc, properties=None):
    """Callback for when the client connects to the broker."""
    if rc == 0:
        logging.info(f"Successfully connected to MQTT Broker at {MQTT_BROKER}")
    else:
        logging.error(f"Failed to connect to MQTT Broker, return code {rc}")

# Initialize the client
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqtt_client.on_connect = on_connect

# --- Set up Flask Web Server ---
app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook_listener():
    """Listens for incoming webhooks and publishes them to MQTT."""
    logging.debug("Received a new request at /webhook endpoint")
    logging.debug(f"Request Headers: {request.headers}")
    
    if not request.is_json:
        logging.warning("Request is not JSON. Returning 415.")
        return jsonify({"error": "Unsupported Media Type: must be application/json"}), 415

    data = request.get_json()
    logging.debug(f"Request body: {json.dumps(data)}")

    if 'alarm' not in data:
        logging.warning("Missing 'alarm' key in JSON body. Returning 400.")
        return jsonify({"error": "Bad Request: JSON body must contain an 'alarm' object"}), 400

    payload_to_publish = data['alarm']
    payload_str = json.dumps(payload_to_publish)

    result = mqtt_client.publish(MQTT_TOPIC, payload_str)
    
    if result.rc == mqtt.MQTT_ERR_SUCCESS:
        logging.debug(f"Successfully published to topic '{MQTT_TOPIC}'")
        return jsonify({"status": "success", "message": f"Published to MQTT topic: {MQTT_TOPIC}"}), 200
    else:
        logging.error(f"Failed to publish message to topic '{MQTT_TOPIC}'. MQTT return code: {result.rc}")
        return jsonify({"status": "error", "message": "Failed to publish to MQTT"}), 500

def main():
    """Main function to parse args, configure, and run the web server."""
    # --- Argument Parsing ---
    # CLI arguments will override Environment variables, which override defaults.
    parser = argparse.ArgumentParser(description="Forward Reolink webhooks to an MQTT topic.")
    parser.add_argument(
        '-p', '--port',
        type=int,
        default=os.getenv("FLASK_PORT", 5000),
        help="Port for the Flask web server. Overrides FLASK_PORT env var. Default: 5000"
    )
    parser.add_argument(
        '-b', '--mqtt-broker',
        type=str,
        default=os.getenv("MQTT_BROKER", "localhost"),
        help="Hostname or IP of the MQTT broker. Overrides MQTT_BROKER env var. Default: localhost"
    )
    parser.add_argument(
        '-mp', '--mqtt-port',
        type=int,
        default=os.getenv("MQTT_PORT", 1883),
        help="Port for the MQTT broker. Overrides MQTT_PORT env var. Default: 1883"
    )
    parser.add_argument(
        '-t', '--mqtt-topic',
        type=str,
        default=os.getenv("MQTT_TOPIC", "home/alarms/camera"),
        help="MQTT topic to publish to. Overrides MQTT_TOPIC env var. Default: home/alarms/camera"
    )
    parser.add_argument(
        '-u', '--mqtt-user',
        type=str,
        default=os.getenv("MQTT_USER", None),
        help="Username for MQTT broker authentication. Overrides MQTT_USER env var."
    )
    parser.add_argument(
        '-pw', '--mqtt-password',
        type=str,
        default=os.getenv("MQTT_PASSWORD", None),
        help="Password for MQTT broker authentication. Overrides MQTT_PASSWORD env var."
    )
    parser.add_argument(
        '-l', '--log-level',
        type=str.upper,
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        default=os.getenv("LOG_LEVEL", "INFO"),
        help="Set the logging level. Overrides LOG_LEVEL env var. Default: INFO"
    )
    args = parser.parse_args()

    # --- Logging Configuration ---
    log_level_str = args.log_level
    numeric_log_level = getattr(logging, log_level_str, logging.INFO)
    logging.basicConfig(
        level=numeric_log_level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logging.info(f"Log level set to {log_level_str}")

    # --- Set Global Configuration ---
    global MQTT_BROKER, MQTT_PORT, MQTT_TOPIC, FLASK_PORT, MQTT_USER, MQTT_PASSWORD
    MQTT_BROKER = args.mqtt_broker
    MQTT_PORT = args.mqtt_port
    MQTT_TOPIC = args.mqtt_topic
    MQTT_USER = args.mqtt_user
    MQTT_PASSWORD = args.mqtt_password
    FLASK_PORT = args.port

    # --- Configure MQTT Client and Connect ---
    if MQTT_USER:
        logging.info(f"Using MQTT username: {MQTT_USER}")
        mqtt_client.username_pw_set(MQTT_USER, MQTT_PASSWORD)

    try:
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
        mqtt_client.loop_start()
    except Exception as e:
        logging.critical(f"Could not connect to MQTT Broker: {e}", exc_info=True)
        exit(1)

    logging.info(f"Starting Flask server on port {FLASK_PORT}")
    logging.info(f"Listening for requests at http://0.0.0.0:{FLASK_PORT}/webhook")
    logging.info(f"Forwarding messages to MQTT topic '{MQTT_TOPIC}' on broker {MQTT_BROKER}:{MQTT_PORT}")
    
    app.run(host='0.0.0.0', port=FLASK_PORT, debug=False)

if __name__ == '__main__':
    main()
