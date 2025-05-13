from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from services.environments_service import EnvironmentsService
from utils.helper import JSONEncoder
import json

router = APIRouter()

@router.get("/environments", response_class=JSONResponse)
def get_environments():
    try:
        service = EnvironmentsService()
        environments = service.get_environments()

        if not environments:
            return JSONResponse(
                status_code=404,
                content={"message": "No environments found"}
            )

        serialized_data = json.dumps({"environments": environments}, cls=JSONEncoder)
        parsed_data = json.loads(serialized_data)

        return JSONResponse(
            status_code=200,
            content=parsed_data
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"message": f"Internal server error: {str(e)}"}
        )