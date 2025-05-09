# from fastapi import APIRouter, HTTPException
# from typing import List
# from services.iot_service import get_iot_data, create_iot_data

# router = APIRouter()

# @router.get("/iot", response_model=List[dict])
# async def read_iot_data():
#     try:
#         data = await get_iot_data()
#         return data
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @router.post("/iot", response_model=dict)
# async def add_iot_data(item: dict):
#     try:
#         new_item = await create_iot_data(item)
#         return new_item
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))
