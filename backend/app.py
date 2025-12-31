import os
import io
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
from PIL import Image

app = FastAPI(title="Fast Image Alt-Text API")

# Allow frontend (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup Gemini (Get your free key at: https://aistudio.google.com/)
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

@app.post("/generate-alt-text")
async def generate_alt_text(
    file: UploadFile = File(...),
    word_limit: int = Form(20)
):
    if not GEMINI_API_KEY:
        return JSONResponse(content={"error": "API Key not configured"}, status_code=500)

    try:
        # 1. Read and optimize image (Resize to save bandwidth/speed)
        image_bytes = await file.read()
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        img.thumbnail((800, 800)) # Resize to max 800px

        # 2. Call Gemini API
        prompt = f"Describe this image for an alt-text attribute in under {word_limit} words."
        response = model.generate_content([prompt, img])
        
        caption = response.text.strip()

        return JSONResponse(content={"alt_text": caption})

    except Exception as e:
        print(f"Error: {e}")
        return JSONResponse(content={"error": "Failed to process image"}, status_code=500)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)