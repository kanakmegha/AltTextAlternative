import os
import base64
import requests
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Scalable CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration for OpenRouter
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# Selected Model: Gemini 2.0 Flash (Free, Fast, and Multimodal)
MODEL_ID = "google/gemini-2.0-flash-001:free"

@app.post("/generate-alt-text")
async def generate_alt_text(file: UploadFile = File(...)):
    if not OPENROUTER_API_KEY:
        raise HTTPException(status_code=500, detail="OpenRouter API key not configured.")

    try:
        # Read and convert image to Base64 (Required for OpenRouter local uploads)
        image_bytes = await file.read()
        base64_image = base64.b64encode(image_bytes).decode("utf-8")
        mime_type = file.content_type or "image/jpeg"

        # Construct the OpenRouter Payload
        payload = {
            "model": MODEL_ID,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text", 
                            "text": "Describe this image in one concise sentence for use as accessibility alt-text. Focus on the main subject and context."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{base64_image}"
                            }
                        }
                    ]
                }
            ]
        }

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }

        # Request to OpenRouter
        response = requests.post(OPENROUTER_URL, headers=headers, json=payload)
        response.raise_for_status()
        
        result = response.json()
        
        # Extract the text response
        if "choices" in result and len(result["choices"]) > 0:
            alt_text = result["choices"][0]["message"]["content"].strip()
            return {"alt_text": alt_text}
        
        return {"error": "No description generated", "details": result}
        
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))