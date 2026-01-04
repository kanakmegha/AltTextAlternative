import os
import base64
import requests
import io
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "").strip()
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# 2026 STABLE FREE VISION MODEL: Xiaomi MiMo V2 Flash
# This is NOT Gemini and NOT Llama. It is highly accurate and free.
MODEL_ID = "xiaomi/mimo-v2-flash:free"

@app.post("/generate-alt-text")
async def generate_alt_text(file: UploadFile = File(...)):
    if not OPENROUTER_API_KEY:
        raise HTTPException(status_code=500, detail="API Key missing.")

    try:
        # 1. Process Image
        file_bytes = await file.read()
        img = Image.open(io.BytesIO(file_bytes))
        if img.mode != "RGB":
            img = img.convert("RGB")
        img.thumbnail((1024, 1024), Image.Resampling.LANCZOS)

        # 2. Encode
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=85)
        base64_image = base64.b64encode(buffer.getvalue()).decode("utf-8")

        # 3. Payload
        payload = {
            "model": MODEL_ID,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Describe this image in one concise sentence for alt-text."},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                        }
                    ]
                }
            ],
            # Adding provider routing bypass to help with 404s
            "route": "fallback" 
        }

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://alttextalternative.onrender.com",
            "X-Title": "AltTextGen"
        }

        response = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=45)
        
        if response.status_code != 200:
            return {"error": f"API Error {response.status_code}", "details": response.text}

        result = response.json()
        if "choices" in result:
            return {"alt_text": result["choices"][0]["message"]["content"].strip()}
        
        return {"error": "Empty Response", "details": result}
        
    except Exception as e:
        return {"error": "Processing failed", "details": str(e)}