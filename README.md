# Azure OpenAI Art Style Profiler

This application analyzes collections of artwork images in different styles using Azure OpenAI Vision (GPT-4.1) and generates a JSON "art style profile" for each style. These profiles can be used to give AI image generators immediate context on how to replicate artwork in a consistent style.

## Purpose

- Automatically extract general art style characteristics from sets of images.
- Generate a JSON profile for each style, omitting specific artwork content, focusing on structure, color, composition, and other style-defining features.
- Use the resulting JSON as a prompt or context for AI image generators to create new images in the same style.

## Setup & Usage

### 1. Clone the repository

```bash
git clone <repo-url>
cd GPT-style-extractor
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install requirements

```bash
pip install -r requirements.txt
```

### 4. Configure Azure OpenAI credentials

Edit the `.env` file and fill in your Azure OpenAI API key, endpoint, and API version:

```
OPENAI_API_KEY=your-azure-openai-api-key-here
OPENAI_API_BASE=https://your-resource-name.openai.azure.com/
OPENAI_API_VERSION=2024-02-15-preview
```

### 5. Place images in the `images/` folder

- Inside the `images/` directory, create a subfolder for each art style (e.g., `images/Impressionism/`, `images/HR Giger/`).
- Place `.jpg`, `.jpeg`, or `.png` images of artworks in each style's subfolder.

Example structure:
```
images/
  Impressionism/
    1.jpg
    2.png
  HR Giger/
    biomech1.jpeg
    biomech2.jpg
```

### 6. Run the script

```bash
python generate_style_profiles.py
```

- The script will process each style folder and generate a JSON profile in the `styles/` directory (e.g., `styles/Impressionism.json`).

### 7. Use the JSON profile in an image generator

- The generated JSON files can be used as context or prompts in AI image generation tools to help replicate the analyzed art style.

## Output

- For each style, a JSON file is created in the `styles/` directory.
- Each JSON profile describes the general characteristics of the style, suitable for guiding AI image generation.

---

**Note:**  
- Requires access to Azure OpenAI GPT-4.1 Vision with image input capability.
- Make sure your Azure credentials and endpoint are correct in the `.env` file.
