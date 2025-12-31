import os
import requests
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add your Vercel URL here
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

HF_TOKEN = os.environ.get("HUGGINGFACE_TOKEN")
# This is the "lightweight" base model
API_URL = "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-base"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

@app.post("/generate-alt-text")
async def generate_alt_text(file: UploadFile = File(...)):
    try:
        image_data = await file.read()
        
        # Send image to Hugging Face
        response = requests.post(API_URL, headers=headers, data=image_data)
        result = response.json()
        
        # BLIP returns a list: [{'generated_text': 'a cat sitting on a table'}]
        if isinstance(result, list) and len(result) > 0:
            return {"alt_text": result[0].get("generated_text", "No description generated.")}
        
        return {"error": "Unexpected response format", "details": result}
        
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))