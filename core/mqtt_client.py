# core/mqtt_client.py
import json, time, uuid, queue
import datetime
import paho.mqtt.client as mqtt
from urllib.parse import urlparse
from core.config import MQTT_BROKER_URL, MONGO_URI, DB_NAME
from pymongo import MongoClient
from repositories.sensor_readings_repository import SensorReadingsRepository


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

    def on_message(self, client, userdata, msg):
        print(f"Received message on topic {msg.topic}")
        
        ###########################################################
        # This is temporary code to handle light sensor data
        # if(msg.topic == "light"):
        #     payload_str = msg.payload.decode('utf-8') 
        #     lines = payload_str.strip().split('\n')
        #     for line in lines:
        #         if "Light ADC Val:" in line:
        #             parts = line.split(":")
        #             if len(parts) == 2:
        #                     value = int(parts[1].strip())
        #                     self.sensor_readings_repo.create({"light": value})
        #                     return
        #             else :
        #                 return
        # return
        ############################################################
        
        data = json.loads(msg.payload.decode())
        print(f"Received message with {data}")
        
        if(msg.topic == "/pot_1/sensors"):
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

        # Find the appropriate queue based on response topic and put the message in the queue
        if msg.topic and msg.topic in self.response_queues:
             self.response_queues[msg.topic].put(data)
             pending_requests_collection.delete_one({"response_topic": msg.topic})  # Remove from pending requests
            
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