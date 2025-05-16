# core/mqtt_client.py
import json, time, uuid, queue
import datetime
import paho.mqtt.client as mqtt
from urllib.parse import urlparse
from core.config import MQTT_BROKER_URL, MONGO_URI, DB_NAME
from pymongo import MongoClient
from repositories.sensor_readings_repository import SensorReadingsRepository
from repositories.environments_repository import EnvironmentsRepository
from repositories.arduinos_repository import ArduinosRepository

# MongoDB Client Setup
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
pending_requests_collection = db["pending_requests"]  # Store pending requests here


class MQTTClient:
    def __init__(self):
        self.client = mqtt.Client(client_id="backend")
        self.response_queues = {}  # Dictionary to hold response queues for each request
        self.client.on_message = self.on_message
        self.sensor_readings_repo = SensorReadingsRepository()
        self.environments_repo = EnvironmentsRepository()
        self.arduinos_repo = ArduinosRepository()

    def handle_sensor_readings(self, data):
        timestamp = time.time()
        dt = datetime.datetime.fromtimestamp(timestamp, tz=datetime.timezone.utc)

        # (ISO 8601)
        formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S")
        # Extract the sensor data from the message

        sensor_data = {
            "temperature": data.get("temperature"),
            "air_humidity": data.get("air_humidity"),
            "soil_humidity": data.get("soil_humidity"),
            "light_intensity": data.get("light_intensity"),
            "plant_pot_id": data.get("plant_pot_id"),
            "timestamp": formatted_time,
        }
        # Store the sensor data in the database
        self.sensor_readings_repo.create(sensor_data)
        return

    def handle_get_pot_data(self, data):
        timestamp = time.time()
        dt = datetime.datetime.fromtimestamp(timestamp, tz=datetime.timezone.utc)
        formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S")

        pot_id = data.get("plant_pot_id")

        update_data = {
            "temperature": data.get("temperature_celsius"),
            "air_humidity": data.get("air_humidity_percentage"),
            "soil_humidity": data.get("soil_humidity_percentage"),
            "light_intensity": data.get("light_intensity_lux"),
            "water_tank_capacity": data.get("water_tank_capacity_ml"),
            "water_level": data.get("water_level_percentage"),
            "measured_at": formatted_time,
        }

        result = self.environments_repo.update_pot(pot_id, update_data)

        print(f"Pots: {self.environments_repo.find_pot_by_id(pot_id)}")

        if result == False:
            # print(f"Pot ID {pot_id} not updated")
            raise ValueError(f"Pot ID {pot_id} not found")

    def on_message(self, client, userdata, msg):
        try:
            print(f"Received message on topic {msg.topic}")

            data = json.loads(msg.payload.decode())
            print(f"Received message with {data}")

            if msg.topic and msg.topic.endswith("/sensors"):
                self.handle_sensor_readings(data)

            if msg.topic and msg.topic.endswith("/data/ok"):
                self.handle_get_pot_data(data)

            # Find the appropriate queue based on response topic and put the message in the queue
            if msg.topic and msg.topic in self.response_queues:
                self.response_queues[msg.topic].put(data)
                pending_requests_collection.delete_one(
                    {"response_topic": msg.topic}
                )  # Remove from pending requests
        except Exception as e:
            print(f"Exception while handling MQTT message: {type(e).__name__} - {e}")
            if msg.topic in self.response_queues:
                self.response_queues[msg.topic].put(
                    {"status": "error", "error": str(e)}
                )

    def subscribe_to_all_topics(self):
        pot_ids = self.arduinos_repo.get_all_arduinos()

        for arduino in pot_ids:
            pot_id = arduino["_id"]
            topic = f"/{pot_id}/sensors"
            print(f"Subscribing to topic: {topic}")
            self.client.subscribe(topic)

    def start(self):
        parsed = urlparse(MQTT_BROKER_URL)
        self.client.connect(parsed.hostname or "mqtt", parsed.port or 1883)
        self.client.loop_start()
        self.subscribe_to_all_topics()

    def send(self, topic: str, payload: dict, timeout=20):
        response_queue = queue.Queue()  # Create a new response queue for each request

        response_topic = f"{topic}/ok"

        self.response_queues[f"{response_topic}"] = response_queue

        # Subscribe to the response topic
        self.client.subscribe(response_topic)

        # Publish the command to the MQTT broker
        self.client.publish(topic, json.dumps(payload))

        pending_requests_collection.insert_one(
            {
                "response_topic": response_topic,
                "topic": topic,
                "payload": payload,
                "status": "pending",  # Initially mark as pending
                "timestamp": time.time(),  # Add timestamp for timeout calculation
            }
        )

        start = time.time()
        while time.time() - start < timeout:
            try:
                response = response_queue.get(timeout=1)
                if response.get("status") == "ok":
                    return response
                else:
                    return {"error": response.get("error", "Unknown error")}
            except queue.Empty:
                continue

        # Timeout or no valid response
        del self.response_queues[response_topic]

        # Update the request in the database to reflect timeout or failure
        pending_requests_collection.update_one(
            {"response_topic": response_topic},
            {"$set": {"status": "timeout", "response": None}},
        )

        return {"error": "Timeout waiting for Arduino response"}


mqtt_client = MQTTClient()
# mqtt_client.start()
