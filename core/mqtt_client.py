# core/mqtt_client.py
import json, time, uuid, queue
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
        if(msg.topic == "light"):
            payload_str = msg.payload.decode('utf-8') 
            lines = payload_str.strip().split('\n')
            for line in lines:
                if "Light ADC Val:" in line:
                    parts = line.split(":")
                    if len(parts) == 2:
                            value = int(parts[1].strip())
                            self.sensor_readings_repo.create({"light": value})
                            return
                    else :
                        return
        
        ############################################################
        data = json.loads(msg.payload.decode())
        correlation_id = data.get("correlation_id")
        print(f"Received message with correlation ID {correlation_id}")

        # Find the appropriate queue based on correlation_id and put the message in the queue
        if correlation_id and correlation_id in self.response_queues:
            self.response_queues[correlation_id].put(data)
            pending_requests_collection.delete_one({"correlation_id": correlation_id})  # Remove from pending requests
            
    def start(self):
        parsed = urlparse(MQTT_BROKER_URL)
        self.client.connect(parsed.hostname or "mqtt", parsed.port or 1883)
        self.client.loop_start()
        #############################################
        self.client.subscribe("light")


    def send(self, topic: str, payload:dict,timeout=5):
        correlation_id = str(uuid.uuid4())
        response_queue = queue.Queue()  # Create a new response queue for each request
        self.response_queues[correlation_id] = response_queue  # Store the response queue by correlation ID

        payload["correlation_id"] = correlation_id
        response_topic = f"{topic}/{correlation_id}"
        
        # Subscribe to the response topic
        self.client.subscribe(response_topic)
        
        # Publish the command to the MQTT broker
        self.client.publish(topic, json.dumps(payload))
        
        pending_requests_collection.insert_one({
            "correlation_id": correlation_id,
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
        del self.response_queues[correlation_id]

        # Update the request in the database to reflect timeout or failure
        pending_requests_collection.update_one(
            {"correlation_id": correlation_id},
            {"$set": {"status": "timeout", "response": None}}
        )
        
        return {"error": "Timeout waiting for Arduino response"}
    



mqtt_client = MQTTClient()
mqtt_client.start()