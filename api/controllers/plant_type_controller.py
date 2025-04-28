from fastapi import APIRouter, HTTPException
from core.config import MONGO_URI, DB_NAME
from pymongo import MongoClient
from pydantic import BaseModel

router = APIRouter()
print("Plant Type Router Initialized")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db["plant_type"]


class PlantTypeRequest(BaseModel):
    plant_type: str
    watering_frequency: int
    water_amount: int

@router.post("/plant_type")
async def create_plant_type(plant_data: PlantTypeRequest):
    """
    Create a new plant type with watering specifications.
    """
    try:
        new_plant_type = {
            "plant_type": plant_data.plant_type,
            "watering_frequency": plant_data.watering_frequency,
            "water_amount": plant_data.water_amount
        }
        
        # Insert into MongoDB
        result = collection.insert_one(new_plant_type)
        
        # Return success response
        return {
            "message": "Plant type created successfully",
            "id": str(result.inserted_id),
            "plant_type": plant_data.plant_type,
            "watering_frequency": plant_data.watering_frequency,
            "water_amount": plant_data.water_amount
        }
    except Exception as e:
        # Log the error here if you have logging set up
        print(f"Error creating plant type: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create plant type: {str(e)}")
    
@router.get("/plant_type_test")
async def test_route():
    return {"message": "Plant type router is working"}