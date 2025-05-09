# core/mqtt_client.py
import json, time, uuid, queue
import datetime
import paho.mqtt.client as mqtt
from urllib.parse import urlparse
from core.config import MQTT_BROKER_URL, MONGO_URI, DB_NAME
from pymongo import MongoClient
from repositories.sensor_readings_repository import SensorReadingsRepository
from repositories.plant_pots_repository import PlantPotsRepository



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
        self.plant_pots_repo = PlantPotsRepository()

    def handle_sensor_readings(self, data):
            timestamp = time.time()
            dt = datetime.datetime.fromtimestamp(timestamp, tz=datetime.timezone.utc)
            
            # (ISO 8601)
            formatted_time = dt.strftime('%Y-%m-%d %H:%M:%S')
            # Extract the sensor data from the message

            sensor_data = {
                "temperature": data.get("temperature"),
                "air_humidity": data.get("air_humidity"),
                "soil_humidity": data.get("soil_humidity"),
                "light_intensity": data.get("light_intensity"),
                "plant_pot_id": data.get("plant_pot_id"),
                "timestamp": formatted_time
            }
            # Store the sensor data in the database
            self.sensor_readings_repo.create(sensor_data)
            return
    
    def handle_get_pot_data(self, data):
        timestamp = time.time()
        dt = datetime.datetime.fromtimestamp(timestamp, tz=datetime.timezone.utc)
        formatted_time = dt.strftime('%Y-%m-%d %H:%M:%S')

        pot_id = data.get("plant_pot_id")
    
        update_data = {
            "temperature_celsius": data.get("temperature_celsius"),
            "air_humidity_percentage": data.get("air_humidity_percentage"),
            "soil_humidity_percentage": data.get("soil_humidity_percentage"),
            "light_intensity_lux": data.get("light_intensity_lux"),
            "water_tank_capacity_ml": data.get("water_tank_capacity_ml"),
            "water_level_percentage": data.get("water_level_percentage"),
            "measured_at": formatted_time,
        }

        result = self.plant_pots_repo.update_pot(pot_id, update_data)
        
        print(f"Pots: {self.plant_pots_repo.find_pot_by_id(pot_id)}")

        if result.matched_count == 0:
            print(f"Pot ID {pot_id} not updated")

    def on_message(self, client, userdata, msg):
        print(f"Received message on topic {msg.topic}")
        
        data = json.loads(msg.payload.decode())
        print(f"Received message with {data}")
        
        if msg.topic and msg.topic.endswith("/sensors"):
            self.handle_sensor_readings(data)


        # Find the appropriate queue based on response topic and put the message in the queue
        if msg.topic and msg.topic in self.response_queues:
             self.response_queues[msg.topic].put(data)
             pending_requests_collection.delete_one({"response_topic": msg.topic})  # Remove from pending requests
             
        if msg.topic and msg.topic.endswith("/data/ok"):
            self.handle_get_pot_data(data)
        
        #return response_queue
    def start(self):
        parsed = urlparse(MQTT_BROKER_URL)
        self.client.connect(parsed.hostname or "mqtt", parsed.port or 1883)
        self.client.loop_start()
        #############################################
        self.client.subscribe("/pot_1/sensors")


    def send(self, topic: str, payload:dict, timeout=20):
        response_queue = queue.Queue()  # Create a new response queue for each request
        
        response_topic = f"{topic}/ok"

        self.response_queues[f"{response_topic}"] = response_queue 

        # Subscribe to the response topic
        self.client.subscribe(response_topic)
        
        # Publish the command to the MQTT broker
        self.client.publish(topic, json.dumps(payload))
        
        pending_requests_collection.insert_one({
            "response_topic": response_topic,
            "topic": topic,
            "payload": payload,
            "status": "pending",  # Initially mark as pending
            "timestamp": time.time()  # Add timestamp for timeout calculation
        })

        start = time.time()
        while time.time() - start < timeout:
            try:
                response = response_queue.get(timeout=1)
                if response.get("status") == "ok":
                    return response
                else:
                    print(f"Error in response: {response}")
            except queue.Empty:
                continue
            
        # Timeout or no valid response
        del self.response_queues[response_topic]

        # Update the request in the database to reflect timeout or failure
        pending_requests_collection.update_one(
            {"response_topic": response_topic},
            {"$set": {"status": "timeout", "response": None}}
        )
        
        return {"error": "Timeout waiting for Arduino response"}
    



mqtt_client = MQTTClient()
mqtt_client.start()