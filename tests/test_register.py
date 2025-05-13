import requests
import json

url = "http://localhost:8000/auth/register"
headers = {
    "Content-Type": "application/json"
}
data = {
    "username": "testuser123",
    "password": "password123",
    "email": "test@example.com"
}

response = requests.post(url, headers=headers, data=json.dumps(data))
print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}")