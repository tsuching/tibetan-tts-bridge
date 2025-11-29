from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from gradio_client import Client
import asyncio
import os

app = FastAPI()

# CORS setup for Flutter Web
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For testing; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize HF client once (point to your HF Space)
SPACE_URL = "https://tsuching-tibetan-tts.hf.space"
client = Client(SPACE_URL)

class TTSRequest(BaseModel):
    text: str

@app.get("/")
def root():
    return {"status": "ok", "message": "Tibetan TTS bridge is running."}

@app.post("/tts")
async def generate_tts(req: TTSRequest):
    print("Received request:", req.text)
    try:
        # Run blocking HF call in a background thread
        raw_result = await asyncio.to_thread(
            client.predict, req.text, api_name="/tts_tibetan"
        )
        print(f"HF raw result: {raw_result}")

        if not raw_result:
            return {"error": "HF Space returned no audio"}

        # Convert local path to hosted URL if needed
        if os.path.isabs(raw_result) and raw_result.startswith("/private"):
            # Grab just the filename
            filename = os.path.basename(raw_result)
            # Construct URL using Space URL
            url = f"{SPACE_URL}/file={filename}"
        else:
            url = raw_result  # Already a URL

        return {"url": url}

    except Exception as e:
        print(f"Error from HF: {e}")
        return {"error": f"HF call failed: {str(e)}"}
