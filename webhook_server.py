import os
import json
import asyncio
import base64
from fastapi import FastAPI, Request, Header
from dotenv import load_dotenv
import websockets

load_dotenv()

ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")
ASSEMBLYAI_REALTIME_URL = "wss://api.assemblyai.com/v2/realtime/ws?sample_rate=16000"

app = FastAPI()

ws = None  # WebSocket object

# Connect to AssemblyAI WebSocket
async def connect_to_assemblyai():
    global ws
    print("🔌 Connecting to AssemblyAI...")

    ws = await websockets.connect(
        ASSEMBLYAI_REALTIME_URL,
        extra_headers={"Authorization": ASSEMBLYAI_API_KEY}
    )

    print("✅ Connected to AssemblyAI")

    # Start listening in background
    asyncio.create_task(receive_transcripts())

# Handle transcripts
async def receive_transcripts():
    global ws
    try:
        async for message in ws:
            data = json.loads(message)
            if data.get("message_type") == "FinalTranscript":
                print("📝 Final Transcript:", data["text"])
    except Exception as e:
        print("❌ Error receiving transcript:", e)

@app.on_event("startup")
async def startup_event():
    await connect_to_assemblyai()

@app.post("/recall-webhook/audio")
async def audio_stream(request: Request, authorization: str = Header(None)):
    global ws

    if authorization != f"Bearer {WEBHOOK_SECRET}":
        return {"error": "Unauthorized"}

    body = await request.body()
    print("📥 Audio data received")

    if not ws:
        return {"error": "WebSocket not connected"}

    try:
        # AssemblyAI expects audio in base64 chunks
        audio_base64 = base64.b64encode(body).decode("utf-8")
        await ws.send(json.dumps({
            "audio_data": audio_base64
        }))
        return {"status": "sent"}
    except Exception as e:
        print("❌ Error sending audio:", e)
        return {"error": str(e)}
