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
        # Run blocking HF call in background
        result = await asyncio.to_thread(client.predict, req.text, api_name="/tts_tibetan")
        print("HF raw result:", result)

        # Ensure we return a public URL
        if isinstance(result, str) and result.startswith("/private"):
            # Prepend the Space URL if Gradio returns a local path
            result = f"https://tsuching-tibetan-tts.hf.space/file={result}"

        return {"url": result}
    except Exception as e:
        print("Error from HF:", e)
        return {"error": f"HF call failed: {str(e)}"}
