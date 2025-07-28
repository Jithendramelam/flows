import os
import asyncio
import websockets
import json
from fastapi import FastAPI, Request, Header
from dotenv import load_dotenv

load_dotenv()

ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")

app = FastAPI()
ws = None  # WebSocket connection to AssemblyAI

import websockets
# from websockets.headers import Headers

async def connect_to_assemblyai():
    print("==> Step 2: Connecting to AssemblyAI...")

    # headers = Headers()
    headers = [("Authorization", f"Bearer {ASSEMBLYAI_API_KEY}")]


    ws = await websockets.connect(url,extra_headers=headers)
    
    print("==> Step 3: Connected to AssemblyAI")
    return ws


async def receive_transcripts():
    global ws
    while True:
        try:
            message = await ws.recv()
            data = json.loads(message)
            if "text" in data and data["message_type"] == "FinalTranscript":
                print("📝 Word:", data["text"])
        except Exception as e:
            print("❌ Error receiving:", e)
            break

@app.post("/recall-webhook/audio")
async def audio_stream(request: Request, authorization: str = Header(None)):
    if authorization != f"Bearer {WEBHOOK_SECRET}":
        return {"error": "Unauthorized"}

    body = await request.body()
    print("==> Step 1: Received request")
    await connect_to_assemblyai()
    print("==> Step 2: Connected to AssemblyAI")
    
    try:
        await ws.send(json.dumps({
            "audio_data": body.decode("latin1")  # AssemblyAI expects base64-encoded audio
        }))
    except Exception as e:
        print("❌ Error sending audio:", e)

# #     return {"status": "ok"}
# from fastapi import FastAPI, Request, HTTPException, status
# from fastapi.responses import JSONResponse
# import logging
# import os

# # Setup logging for Railway (logs to stdout)
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# app = FastAPI()


# @app.post("/recall-webhook/audio")
# async def receive_audio(request: Request):
#     try:
#         # Validate content-type
#         content_type = request.headers.get("content-type", "")
#         if "audio" not in content_type:
#             raise HTTPException(status_code=415, detail="Unsupported Media Type. Expected audio content.")

#         # Read audio bytes
#         audio_bytes = await request.body()

#         if not audio_bytes:
#             raise HTTPException(status_code=400, detail="No audio data received.")

#         # Create output folder if not exists
#         os.makedirs("received_audio", exist_ok=True)

#         # Save the audio file
#         output_path = "received_audio/received.wav"
#         with open(output_path, "wb") as f:
#             f.write(audio_bytes)

#         logger.info(f"Saved audio to {output_path}")
#         return {"status": "received", "path": output_path}

#     except HTTPException as e:
#         logger.warning(f"HTTP error: {e.detail}")
#         raise
#     except Exception as e:
#         logger.exception("Unhandled error while processing audio.")
#         raise HTTPException(status_code=500, detail="Internal Server Error")


# # Optional: Global error handler for unhandled exceptions
# @app.exception_handler(Exception)
# async def global_exception_handler(request: Request, exc: Exception):
#     logger.error(f"Global error: {exc}")
#     return JSONResponse(
#         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#         content={"message": "Oops! Something went wrong."}
#     )
