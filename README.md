# AltTextAlternative 🖼️ ✍️

**AltTextAlternative** is a high-efficiency, AI-powered API designed to generate descriptive accessibility alt-text for images. Built with **FastAPI** and powered by the **Salesforce BLIP** (Bootstrapping Language-Image Pre-training) model via Hugging Face, it provides a stable, free-forever solution for web accessibility.

## 🚀 Key Features
- **High-Accuracy Descriptions:** Uses the `blip-image-captioning-large` model for human-like captions.
- **TIF/TIFF Support:** Custom processing pipeline to handle heavy medical and scientific image formats.
- **Resource Optimized:** Automatic image compression to save bandwidth and stay within API quotas.
- **Free Forever:** Optimized for the Hugging Face Serverless Inference API (~1,000 requests/day).

---

## 🛠️ Architecture & Components

The system is composed of three main layers to ensure stability and cost-efficiency:

1.  **FastAPI Backend:** Provides the interface for HTTP `multipart/form-data` requests.
2.  **Pillow Processing Engine:** A middleware layer that converts heavy or unsupported formats (like `.tif`) into optimized, RGB-encoded JPEGs (resized to 800px).
3.  **HF Inference Layer:** Communicates with Hugging Face's global GPU cluster using a "retry-on-load" strategy to handle model cold starts.



---

## 🚦 Getting Started

### 1. Prerequisites
- Python 3.9+
- A Hugging Face Access Token. Create one for free at [hf.co/settings/tokens](https://huggingface.co/settings/tokens) (ensure it has **Inference** permissions).

### 2. Environment Setup
Set your API key as an environment variable in your hosting platform (Render, Vercel, or locally):
```env
HF_API_KEY=your_huggingface_token_here
```
## 🚦 Local Installation

To get the project running on your local machine, follow these steps:

### 1. Prerequisites
- **Python 3.9 or higher** installed.
- A **Hugging Face Access Token** with `Inference` permissions.

### 2. Setup Procedure
```bash
# Clone your repository
git clone [https://github.com/your-username/alttextalternative.git](https://github.com/your-username/alttextalternative.git)
cd alttextalternative

# Create and activate a virtual environment
python -m venv venv

# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install required libraries
pip install -r requirements.txt
```
### 3. Environment Configuration
To keep your API keys secure, use a `.env` file in the root directory. **Never commit your `.env` file to GitHub.**

Create a file named `.env`:
```env
HF_API_KEY=hf_your_actual_token_here
```
