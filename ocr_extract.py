import pytesseract
from PIL import Image

def extract_fields(image_path):
    img = Image.open(image_path)
    raw_text = pytesseract.image_to_string(img)

    title = ""
    author = ""
    for line in raw_text.split("\n"):
        if "by" in line.lower():
            parts = line.split("by")
            title = parts[0].strip()
            author = parts[1].strip() if len(parts) > 1 else ""

    return {
        "title": title,
        "author": author,
        "raw": raw_text
    }