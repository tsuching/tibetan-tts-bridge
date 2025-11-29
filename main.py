from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from gradio_client import Client
import requests
import time
import asyncio

# Initialize FastAPI
app = FastAPI()

# Allow your Flutter Web app to call this backend.
# Add your dev origin (http://localhost:xxxx) and production origin(s) here.
origins = [
    "http://localhost:3000",
    "http://localhost:4000",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:4000",
    # Add your deployed Flutter Web domain here when you have it
    "*",   # ← Optional: enable if Render blocks you
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ← For testing, allow all origins. Change this in production.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize HF client **once** at module level
client = Client("tsuching/Tibetan-tts")

class TTSRequest(BaseModel):
    text: str

@app.get("/")
def root():
    return {"status": "ok", "message": "Tibetan TTS bridge is running."}

@app.post("/tts")
async def generate_tts(req: TTSRequest):
    result = await asyncio.to_thread(client.predict, req.text, api_name="/tts_tibetan")
    print("Received request:", req.text)

    try:        
        # Create client only when needed (lazy load)
        #client = Client("https://tsuching-tibetan-tts.hf.space/")

        result = client.predict(req.text, api_name="/tts_tibetan")
        print(f"HF raw result: {result}")  # Debug log

        #if client is None:
        #    client = Client("tsuching/Tibetan-tts")


        # Call the named API you confirmed: /tts_tibetan
        result = client.predict(req.text, api_name="/tts_tibetan")
        print(f"HF raw result: {result}")  # Debug log

        if not result:
            # Retry once if empty
            time.sleep(2)
            result = client.predict(req.text, api_name="/tts_tibetan")

        if not result:
            return {"error": "HF Space returned no audio"}

        # 'result' is a hosted file URL like https://.../file=/tmp/gradio/output.wav
        if isinstance(result, str) and result.startswith("/"):
            result = f"https://tsuching-tibetan-tts.hf.space{result}" #/file={result}"

        return {"url": result}
    except Exception as e:
        print(f"Error from HF: {e}")
        return {"error": f"HF call failed: {str(e)}"}
