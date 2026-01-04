import os
import base64
import requests
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware

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

# NEW MODEL: Llama 3.2 11B Vision (Free, Accurate, and very Fast)
MODEL_ID = "meta-llama/llama-3.2-11b-vision-instruct:free"

@app.post("/generate-alt-text")
async def generate_alt_text(file: UploadFile = File(...)):
    if not OPENROUTER_API_KEY:
        raise HTTPException(status_code=500, detail="OPENROUTER_API_KEY missing")

    try:
        # Read file
        image_bytes = await file.read()
        
        # Convert to Base64
        base64_image = base64.b64encode(image_bytes).decode("utf-8")
        
        # Determine MIME type
        mime_type = file.content_type or "image/jpeg"

        # Llama 3.2 Vision Payload
        payload = {
            "model": MODEL_ID,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text", 
                            "text": "Write a clean, descriptive alt-text for this image. Be concise and focus on the visual facts."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            "temperature": 0.5, # Keeps descriptions factual
            "max_tokens": 100
        }

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://alttextapp.com", # Required by some OpenRouter models
        }

        # Request
        response = requests.post(
            OPENROUTER_URL,
            headers=headers,
            json=payload,
            timeout=30
        )

        if response.status_code != 200:
            # This helps you see the REAL error if it's a 404 or 401
            return {"error": f"API Error {response.status_code}", "details": response.text}

        result = response.json()
        
        if "choices" in result and len(result["choices"]) > 0:
            content = result["choices"][0]["message"]["content"]
            return {"alt_text": content.strip()}
        
        return {"error": "No description returned", "details": result}
        
    except Exception as e:
        print(f"Server Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))