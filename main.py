from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from gradio_client import Client

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
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prepare the client to your Space
#client = Client("tsuching/Tibetan-tts")


class TTSRequest(BaseModel):
    text: str

@app.get("/")
def root():
    return {"status": "ok", "message": "Tibetan TTS bridge is running."}

@app.post("/tts")
def generate_tts(req: TTSRequest):
    try:
        # Create client only when needed (lazy load)
        client = Client("https://tsuching-tibetan-tts.hf.space/")
        # Call the named API you confirmed: /tts_tibetan
        result = client.predict(req.text, api_name="/tts_tibetan")
        # 'result' is a hosted file URL like https://.../file=/tmp/gradio/output.wav
        if isinstance(result, str) and result.startswith("/"):
            result = f"https://tsuching-tibetan-tts.hf.space/file={result}"
        return {"url": result}
    except Exception as e:
        return {"error": f"HF call failed: {str(e)}"}
