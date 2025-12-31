import os
import io
import google.generativeai as genai
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import StreamingResponse
from PIL import Image

app = FastAPI()

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

async def stream_alt_text(img, limit):
    prompt = f"Describe this image for alt-text in under {limit} words."
    # We use stream=True to get parts of the text as they are created
    response = model.generate_content([prompt, img], stream=True)
    for chunk in response:
        yield chunk.text

@app.post("/generate-alt-text")
async def generate_alt_text(file: UploadFile = File(...), word_limit: int = Form(20)):
    # 1. Read image (uses very little RAM)
    image_bytes = await file.read()
    img = Image.open(io.BytesIO(image_bytes))
    
    # 2. Return a StreamingResponse using our generator
    return StreamingResponse(stream_alt_text(img, word_limit), media_type="text/plain")