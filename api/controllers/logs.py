# # backend/api/logs.py

# from fastapi import APIRouter
# from db.session import db

# router = APIRouter()

# @router.get("/logs")
# def get_logs():
#     """
#     Return all logs from the MongoDB 'logs' collection.
#     """
#     cursor = db["logs"].find()
#     # Convert the cursor to a list of documents
#     logs_list = list(cursor)
#     # Convert ObjectId to string if needed
#     for doc in logs_list:
#         doc["_id"] = str(doc["_id"])
#     return {"logs": logs_list}
