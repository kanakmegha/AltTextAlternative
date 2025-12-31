import os
import io
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
from PIL import Image

app = FastAPI()

# --- 1. Fix CORS ---
# Replace the URL below with your actual Vercel URL
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://alt-text-alternative-6s2t-qzje1dq4t.vercel.app" 
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 2. Initialize Gemini ---
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

@app.post("/generate-alt-text")
async def generate_alt_text(
    file: UploadFile = File(...), 
    word_limit: int = Form(20)
):
    try:
        # Read the uploaded file bytes
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="Empty file uploaded")

        # Open image and handle formats like TIFF or RGBA
        img = Image.open(io.BytesIO(content))
        
        # Convert to RGB (required for many AI models and prevents 400 errors)
        if img.mode != 'RGB':
            img = img.convert('RGB')

        # Generate alt text using Gemini
        prompt = f"Describe this image for alt-text in under {word_limit} words."
        response = model.generate_content([prompt, img])
        
        return {"alt_text": response.text}
    
    except Exception as e:
        print(f"Error: {str(e)}") # Visible in Render logs
        return HTTPException(status_code=500, detail=str(e))