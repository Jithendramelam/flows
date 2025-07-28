import requests
import os
from dotenv import load_dotenv

load_dotenv()

RECALL_API_KEY = os.getenv("RECALL_API_KEY")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")
NGROK_URL = os.getenv("NGROK_URL")  # Example: https://abc123.ngrok.io

headers = {
    "Authorization": f"Token {RECALL_API_KEY}",
    "Content-Type": "application/json"
}

meeting_url = input("Enter the meeting URL: ")

payload = {
    "meeting_url": meeting_url,
    "webhook_url": f"{NGROK_URL}/recall-webhook/audio",
    "webhook_headers": {
        "Authorization": f"Bearer {WEBHOOK_SECRET}"
    },
    "recording_config": {
        "transcript": {
            "provider": {
                "meeting_captions": {}
            }
        }
    }
}

print("🚀 Sending bot to join the meeting (WebSocket mode)...")
response = requests.post("https://us-west-2.recall.ai/api/v1/bot/", headers=headers, json=payload)
print("📡 Status Code:", response.status_code)
print("📨 Response:", response.text)
