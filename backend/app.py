import os
import io
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
from PIL import Image

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. SETUP GOOGLE AI
# Make sure your environment variable name is GEMINI_API_KEY
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
genai.configure(api_key=GEMINI_API_KEY)

# Using Gemini 2.0 Flash (Fastest and 100% Free on AI Studio)
# Change from 'gemini-2.0-flash' to 'gemini-1.5-flash'
model = genai.GenerativeModel('gemini-1.5-flash')

@app.post("/generate-alt-text")
async def generate_alt_text(file: UploadFile = File(...)):
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY missing in environment.")

    try:
        # 2. PROCESS IMAGE (The TIF Fix)
        file_bytes = await file.read()
        img = Image.open(io.BytesIO(file_bytes))
        
        # Convert TIF/PNG to standard RGB
        if img.mode != "RGB":
            img = img.convert("RGB")
        
        # Keep size reasonable for speed
        img.thumbnail((1024, 1024))
        
        # 3. GENERATE ALT TEXT
        # Google SDK handles PIL images directly!
        response = model.generate_content([
            "Write a concise, factual alt-text for this image for accessibility.",
            img
        ])

        if response.text:
            return {"alt_text": response.text.strip()}
        
        return {"error": "No text generated"}

    except Exception as e:
        print(f"Error: {str(e)}")
        return {"error": "Failed to process image", "details": str(e)}