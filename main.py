from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from gradio_client import Client
import asyncio

app = FastAPI()

# CORS setup for Flutter Web
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For testing; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize HF client once
client = Client("tsuching/Tibetan-tts")

class TTSRequest(BaseModel):
    text: str

@app.get("/")
def root():
    return {"status": "ok", "message": "Tibetan TTS bridge is running."}

@app.post("/tts")
async def generate_tts(req: TTSRequest):
    print("Received request:", req.text)
    try:
        # Run the blocking HF call in a background thread
        raw_result = await asyncio.to_thread(client.predict, req.text, api_name="/tts_tibetan")
        print(f"HF raw result: {raw_result}")  # debug log

        # The gradio_client now returns a public URL
        url = raw_result
        return {"url": url}

    except Exception as e:
        print(f"Error from HF: {e}")
        return {"error": f"HF call failed: {str(e)}"}

