# app.py
import os
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from transformers import Blip2Processor, Blip2ForConditionalGeneration
from PIL import Image
import torch
import io

# Initialize FastAPI
app = FastAPI(title="Image Alt-Text API")

# Allow frontend (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all origins; tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model & processor once at startup
device = "cuda" if torch.cuda.is_available() else "cpu"
model_name = "Salesforce/blip2-opt-2.7b"  # Big model (slow but accurate)

processor = Blip2Processor.from_pretrained(model_name)
model = Blip2ForConditionalGeneration.from_pretrained(
    model_name,
    torch_dtype=torch.float16 if device == "cuda" else torch.float32
)
model.to(device)

@app.post("/generate-alt-text")
async def generate_alt_text(
    file: UploadFile = File(...),
    word_limit: int = Form(20)
):
    try:
        # Read uploaded image
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        # Preprocess
        inputs = processor(images=image, return_tensors="pt").to(device)

        # Generate caption
        output = model.generate(**inputs, max_new_tokens=word_limit + 5)
        caption = processor.decode(output[0], skip_special_tokens=True)

        # Enforce word limit
        caption_words = caption.split()
        if len(caption_words) > word_limit:
            caption = " ".join(caption_words[:word_limit])

        return JSONResponse(content={"alt_text": caption})

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


# Run with uvicorn when executed directly
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # Use Render's PORT env variable
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)
