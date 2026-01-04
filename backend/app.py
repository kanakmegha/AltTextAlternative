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

# Configuration
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "").strip()
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# MODEL: Qwen 2.5 VL (High Accuracy, Fast, Non-Gemini/Llama)
MODEL_ID = "qwen/qwen2.5-vl-72b-instruct:free"

@app.post("/generate-alt-text")
async def generate_alt_text(file: UploadFile = File(...)):
    if not OPENROUTER_API_KEY:
        raise HTTPException(status_code=500, detail="API Key missing in environment.")

    try:
        # 1. Process Image (Critical for TIF compatibility)
        file_bytes = await file.read()
        img = Image.open(io.BytesIO(file_bytes))

        if img.mode != "RGB":
            img = img.convert("RGB")
        
        # Resize to standard size for faster API transmission
        img.thumbnail((1024, 1024), Image.Resampling.LANCZOS)

        # 2. Encode to Base64
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=85)
        base64_image = base64.b64encode(buffer.getvalue()).decode("utf-8")

        # 3. Payload for Qwen VL
        payload = {
            "model": MODEL_ID,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Describe this image in one concise sentence for accessibility alt-text."},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                        }
                    ]
                }
            ],
            "temperature": 0.3 # Lower temperature for more factual descriptions
        }

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://alttextalternative.onrender.com",
            "X-Title": "AltTextGenerator"
        }

        # 4. Request
        response = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=50)
        
        if response.status_code != 200:
            return {"error": f"API Error {response.status_code}", "details": response.text}

        result = response.json()
        
        if "choices" in result and len(result["choices"]) > 0:
            return {"alt_text": result["choices"][0]["message"]["content"].strip()}
        
        return {"error": "Model returned no text", "details": result}
        
    except Exception as e:
        return {"error": "Server-side processing failed", "details": str(e)}