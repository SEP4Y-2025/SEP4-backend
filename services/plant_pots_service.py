# service/pots_service.py

from dto.plant_pot_dto import AddPlantPotRequest, PlantPotResponse
from repositories.plant_pots_repository import PlantPotsRepository
from repositories.arduinos_repository import ArduinosRepository
from core.mqtt_client import mqtt_client
from repositories.plant_types_repository import PlantTypesRepository
from repositories.sensor_readings_repository import SensorReadingsRepository

class PlantPotsService:
    def __init__(self):
        self.plant_pots_repo = PlantPotsRepository()
        self.arduinos_repo = ArduinosRepository()
        self.plant_types_repo = PlantTypesRepository()
        self.sensor_readings_repo = SensorReadingsRepository()

    def add_plant_pot(self, environment_id : str, pot: AddPlantPotRequest) -> PlantPotResponse:
        if not self.arduinos_repo.is_registered(pot.pot_id):
            raise ValueError("Unknown or unregistered Arduino")

        print("Registered pot - good\n")
        
        # Get full plant type details from DB
        plant_type = self.plant_types_repo.get(pot.plant_type_id)
        if not plant_type:
            raise ValueError("Invalid plant type ID")

        # Send MQTT command to hardware
        payload = {
            "command": "pots/add",
            "pot_id": pot.pot_id,
            "frequency": plant_type["watering_frequency"],
            "dosage": plant_type["water_dosage"]
        }
        
        print("Sending command to MQTT broker:", payload)
        
        result = mqtt_client.send(f"pots/{pot.pot_id}/add", payload)

        if result.get("error"):
            raise ValueError(result["error"])

        # Store in DB
        pot_doc = {
            "_id": pot.pot_id,
            "plant_pot_label": pot.plant_pot_label,
            "plant_type_id": pot.plant_type_id,
            "environment_id": environment_id 
        }
        
        self.plant_pots_repo.insert_pot(pot_doc)
        self.arduinos_repo.mark_active(pot.pot_id)

        # Return response
        return PlantPotResponse(
            message="Pot added successfully",
            pot_id=pot.pot_id,
            plant_pot_label=pot.plant_pot_label,
            plant_type_id=pot.plant_type_id,
            plant_type_name=plant_type["plant_type_name"],
            watering_frequency=plant_type["watering_frequency"],
            water_dosage=plant_type["water_dosage"],
            environment_id=pot_doc["environment_id"]
        )

    def delete_plant_pot(self, pot_id: str) -> bool:
        if not self.arduinos_repo.is_registered(pot_id):
            raise ValueError("Unknown or unregistered Arduino")

        print("Registered pot - good\n")

        # Get the pot from DB first to gather full info (before deletion)
        pot = self.plant_pots_repo.get_pot(pot_id)
        if not pot:
            raise ValueError("Plant pot not found")

        # Send MQTT delete command
        payload = {
            "command": "pots/delete",
            "pot_id": pot_id
        }
        result = mqtt_client.send(f"pots/{pot_id}/delete", payload)

        if result.get("error"):
            raise ValueError(result["error"])
        
        # Delete sensor readings related to this pot from the sensor_readings collection
        deleted_count = self.sensor_readings_repo.delete_by_pot(pot_id)
        print(f"Deleted {deleted_count} sensor readings associated with pot {pot_id}")

        # Delete from DB
        self.plant_pots_repo.delete_pot(pot_id)
        self.arduinos_repo.mark_inactive(pot_id)

        return True
