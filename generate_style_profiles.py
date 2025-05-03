import os
import json
import base64
from pathlib import Path
from openai import AzureOpenAI, OpenAIError
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")
OPENAI_API_VERSION = os.getenv("OPENAI_API_VERSION")

if not OPENAI_API_KEY or not OPENAI_API_BASE or not OPENAI_API_VERSION:
    raise EnvironmentError(
        "Missing one or more required environment variables: OPENAI_API_KEY, OPENAI_API_BASE, OPENAI_API_VERSION"
    )

# Set up your Azure OpenAI client using .env configuration
client = AzureOpenAI(
    api_key=OPENAI_API_KEY,
    azure_endpoint=OPENAI_API_BASE,
    default_headers={"api-key": OPENAI_API_KEY},
    api_version=OPENAI_API_VERSION,
)

IMAGES_DIR = Path("images")
STYLES_DIR = Path("styles")
MODEL_NAME = "gpt-4.1"

def process_style_folder(style_folder_path):
    style_name = style_folder_path.name
    image_paths = list(style_folder_path.glob("*.jpg")) + list(style_folder_path.glob("*.jpeg")) + list(style_folder_path.glob("*.png"))
    if not image_paths:
        print(f"[INFO] No images found in {style_folder_path}, skipping.")
        return

    try:
        print(f"[INFO] Processing style: {style_name} ({len(image_paths)} images)")
        json_profile = analyze_images_with_gpt(image_paths, style_name)
        if json_profile:
            save_json_profile(style_name, json_profile)
    except Exception as e:
        print(f"[ERROR] Failed to process style '{style_name}': {e}")

def analyze_images_with_gpt(image_paths, style_name):
    prompt = (
        f"Create a JSON profile. This JSON profile should be an 'art style' profile that extracts data from these pieces of art ({style_name}), "
        "so that I can send the JSON to an AI to give immediate context on how to replicate such artwork with consistent style. "
        "It should not include specific art data, such as the contents of the specific artworks or anything specific to each piece of artwork. "
        "It should include the general art style, the structure, or anything that will help an AI replicate such artwork."
    )

    # Prepare the message content for the API call
    content = [{"type": "text", "text": prompt}]
    for img_path in image_paths:
        try:
            with open(img_path, "rb") as img_file:
                img_bytes = img_file.read()
            img_base64 = base64.b64encode(img_bytes).decode("utf-8")
            # Use correct MIME type for jpg/jpeg
            ext = img_path.suffix.lower()
            if ext in [".jpg", ".jpeg"]:
                mime = "jpeg"
            elif ext == ".png":
                mime = "png"
            else:
                mime = ext[1:] if ext.startswith(".") else ext
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/{mime};base64,{img_base64}"
                }
            })
        except Exception as e:
            print(f"[ERROR] Could not read image {img_path}: {e}")

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": content}],
            max_tokens=1000,
        )
        # Extract the JSON from the model's response
        reply = response.choices[0].message.content
        # Try to parse the JSON from the reply
        try:
            json_start = reply.find("{")
            json_end = reply.rfind("}") + 1
            json_str = reply[json_start:json_end]
            json_profile = json.loads(json_str)
            return json_profile
        except Exception as e:
            print(f"[ERROR] Could not parse JSON from model response: {e}\nRaw response: {reply}")
            return None
    except OpenAIError as e:
        print(f"[ERROR] OpenAI API error: {e}")
        return None

def save_json_profile(style_name, json_data):
    STYLES_DIR.mkdir(exist_ok=True)
    out_path = STYLES_DIR / f"{style_name}.json"
    try:
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        print(f"[SUCCESS] Saved style profile: {out_path}")
    except Exception as e:
        print(f"[ERROR] Could not save JSON profile for '{style_name}': {e}")

def main():
    if not IMAGES_DIR.exists():
        print(f"[ERROR] Images directory '{IMAGES_DIR}' does not exist.")
        return

    for style_folder in IMAGES_DIR.iterdir():
        if style_folder.is_dir():
            process_style_folder(style_folder)

if __name__ == "__main__":
    main()
