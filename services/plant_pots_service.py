# service/pots_service.py

from models.plant_pot import (
    AddPlantPotRequest,
    AddPlantPotResponse,
    GetPlantPotResponse,
)
from repositories.environments_repository import EnvironmentsRepository
from repositories.arduinos_repository import ArduinosRepository
from repositories.plant_types_repository import PlantTypesRepository
from repositories.sensor_readings_repository import SensorReadingsRepository
from core.mqtt_client import mqtt_client
import json, time, uuid, queue
import datetime


class PlantPotsService:
    def __init__(self):
        self.environments_repo = EnvironmentsRepository()
        self.arduinos_repo = ArduinosRepository()
        self.plant_types_repo = PlantTypesRepository()
        self.sensor_readings_repo = SensorReadingsRepository()

    def add_plant_pot(
        self, environment_id: str, pot: AddPlantPotRequest
    ) -> AddPlantPotResponse:

        if pot.plant_pot_label.strip() == "":
            raise ValueError("Invalid plant pot label")

        if not self.arduinos_repo.is_registered(pot.pot_id):
            raise ValueError("Unknown or unregistered Arduino")

        print("Registered pot - good\n")

        # Get full plant type details from DB
        plant_type = self.plant_types_repo.get_plant_type_by_id(pot.plant_type_id)
        if not plant_type:
            raise ValueError("Invalid plant type ID")

        # Send MQTT command to hardware
        payload = {
            "watering_frequency": plant_type["watering_frequency"],
            "water_dosage": plant_type["water_dosage"],
        }

        print("Sending command to MQTT broker:", payload)

        result = mqtt_client.send(f"/{pot.pot_id}/activate", payload)

        if result.get("error"):
            raise ValueError(result["error"])

        timestamp = time.time()
        dt = datetime.datetime.fromtimestamp(timestamp, tz=datetime.timezone.utc)

        # (ISO 8601)
        formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S")
        # Extract the sensor data from the message

        # Store in DB
        pot_doc = {
            "pot_id": pot.pot_id,
            "label": pot.plant_pot_label,
            "plant_type_id": pot.plant_type_id,
            "environment_id": environment_id,
            "soil_humidity": 0,
            "air_humidity": 0,
            "temperature": 0,
            "light_intensity": 0,
            "water_tank_capacity": 0,
            "water_level": 0,
            "measured_at": formatted_time,
        }

        self.environments_repo.insert_pot(environment_id, pot_doc)
        self.arduinos_repo.mark_active(pot.pot_id)

        return AddPlantPotResponse(
            message="Pot added successfully",
            pot_id=pot.pot_id,
            plant_pot_label=pot.plant_pot_label,
            plant_type_id=pot.plant_type_id,
            plant_type_name=plant_type["name"],
            watering_frequency=plant_type["watering_frequency"],
            water_dosage=plant_type["water_dosage"],
            environment_id=pot_doc["environment_id"],
        )

    def get_plant_pot_by_id(self, env_id: str, pot_id: str) -> GetPlantPotResponse:
        payload = {}
        result = mqtt_client.send(f"/{pot_id}/data", payload)

        if result.get("error"):
            if result["error"] == "Timeout waiting for Arduino response":
                raise ValueError("Timeout waiting for Arduino response")
            else:
                raise ValueError(result["error"])

        pot = self.environments_repo.find_pot_by_id(pot_id)
        if not pot:
            raise ValueError(f"Plant pot with ID {pot_id} not found")

        plant_type = self.plant_types_repo.get_plant_type_by_id(pot["plant_type_id"])

        if not plant_type:
            raise ValueError("Invalid plant type ID")

        return GetPlantPotResponse(
            pot_id=pot_id,
            plant_pot_label=pot["label"],
            plant_type_id=pot["plant_type_id"],
            plant_type_name=plant_type["name"],
            watering_frequency=plant_type["watering_frequency"],
            water_dosage=plant_type["water_dosage"],
            environment_id=pot["environment_id"],
            soil_humidity_percentage=pot["soil_humidity"],
            air_humidity_percentage=pot["air_humidity"],
            temperature_celsius=pot["temperature"],
            light_intensity_lux=pot["light_intensity"],
            water_tank_capacity_ml=pot["water_tank_capacity"],
            water_level_percentage=pot["water_level"],
            measured_at=pot["measured_at"],
        )

    def get_pots_by_environment(self, environment_id: str):
        return self.environments_repo.get_pots_by_environment(environment_id)

    def delete_plant_pot(self, pot_id: str) -> bool:
        if not self.arduinos_repo.is_registered(pot_id):
            raise ValueError("Unknown or unregistered Arduino")

        print("Registered pot - good\n")

        # Get the pot from DB first to gather full info (before deletion)
        pot = self.environments_repo.find_pot_by_id(pot_id)
        if not pot:
            raise ValueError("Plant pot not found")

        # Send MQTT delete command
        payload = {}
        result = mqtt_client.send(f"/{pot_id}/deactivate", payload)

        if result.get("error"):
            raise ValueError(result["error"])

        # Delete sensor readings related to this pot from the sensor_readings collection
        deleted_count = self.sensor_readings_repo.delete_by_pot(pot_id)
        print(f"Deleted {deleted_count} sensor readings associated with pot {pot_id}")

        # Delete from DB
        self.environments_repo.delete_pot(pot_id)
        self.arduinos_repo.mark_inactive(pot_id)

        return True
