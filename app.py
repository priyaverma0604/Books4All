from flask import Flask, render_template, request
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import base64
import os
import easyocr
import re
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (
    Mail, Attachment, FileContent, FileName, FileType, Disposition
)
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "trivedi.abhaya10@gmail.com")

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# EasyOCR Reader
reader = easyocr.Reader(['en'], gpu=False)
request_list = [
    {"title": "India After Gandhi", "author": "Ramachandra Guha", "status": "Requested", "action": ""},
    {"title": "Wings of Fire", "author": "A.P.J. Abdul Kalam", "status": "Completed", "action": "Review"},
]

# ---------------------- CERTIFICATE GENERATION ---------------------- #
def generate_certificate(name):
    TEMPLATE_PATH = "static/images/certificate_template.png"
    FONT_PATH = "/System/Library/Fonts/Supplemental/Arial.ttf"  # macOS default

    try:
        cert = Image.open(TEMPLATE_PATH).convert("RGB")
    except FileNotFoundError:
        print(f"❌ Template not found at {TEMPLATE_PATH}")
        return None

    draw = ImageDraw.Draw(cert)

    try:
        font_large = ImageFont.truetype(FONT_PATH, size=100)
    except OSError:
        print(f"❌ Could not open font at {FONT_PATH}")
        return None

    image_width, image_height = cert.size
    bbox = font_large.getbbox(name)
    text_width = bbox[2] - bbox[0]

    x = (image_width - text_width) / 2
    y = 700
    draw.text((x, y), name, font=font_large, fill="black")

    safe_name = name.replace(" ", "_").replace("/", "_")
    filename = f"cert_{safe_name}.png"
    output_path = os.path.join("static", filename)
    cert.save(output_path)
    print(f"✅ Certificate saved: {output_path}")
    return output_path

def send_certificate_email(recipient_email, name, cert_path):
    with open(cert_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    message = Mail(
        from_email=SENDER_EMAIL,
        to_emails=recipient_email,
        subject="Books4All - Certificate of Appreciation",
        html_content=f"""
        <p>Dear {name},</p>
        <p>Thank you for your generous donation to <strong>Books4All</strong>!</p>
        <p>Please find your certificate of appreciation attached.</p>
        <p>Warm regards,<br>Books4All Team</p>
        """
    )

    attachment = Attachment()
    attachment.file_content = FileContent(encoded)
    attachment.file_type = FileType("image/png")
    attachment.file_name = FileName("Books4All_Certificate.png")
    attachment.disposition = Disposition("attachment")
    message.attachment = attachment

    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(f"✅ Email sent to {recipient_email} | Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Email error: {str(e)}")

# ---------------------- OCR + BOOK INFO EXTRACTION ---------------------- #
def extract_text_easyocr(image_path):
    try:
        results = reader.readtext(image_path)
        return "\n".join([res[1] for res in results])
    except Exception as e:
        print(f"EasyOCR error: {e}")
        return ""

def predict_genre(text):
    text = text.lower()
    if "math" in text:
        return "Mathematics"
    elif "history" in text:
        return "History"
    elif "science" in text:
        return "Science"
    elif "grammar" in text or "language" in text:
        return "Language"
    elif "biology" in text or "chemistry" in text:
        return "Biology/Chemistry"
    return "General"

def parse_book_info(text):
    book_info = {'title': '', 'author': '', 'isbn': '', 'language': '', 'publisher': '', 'publication_date': '', 'condition': '', 'grade_level': ''}

    # Title and Author
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    book_info['title'] = lines[0] 
    for line in lines:
        if "by" in line.lower():
            parts = line.split("by")
            book_info['title'] = parts[0].strip()
            book_info['author'] = parts[1].strip() if len(parts) > 1 else ""
            break

    # ISBN
    isbn_pattern = r'(?:ISBN(?:-1[03])?:?\s*)?(\d{9,13}[\dX]?)'
    match = re.search(isbn_pattern, text)
    if match:
        book_info['isbn'] = match.group(1)

    # Publisher and Date
    pub_match = re.search(r'published by\s+(.*)', text, re.IGNORECASE)
    if pub_match:
        book_info['publisher'] = pub_match.group(1).strip()

    date_match = re.search(r'(?:copyright|©)\s*(\d{4})', text, re.IGNORECASE)
    if date_match:
        book_info['publication_date'] = date_match.group(1)

    # Language
    if re.search(r'spanish|español', text, re.IGNORECASE):
        book_info['language'] = 'Spanish'
    elif re.search(r'french|français', text, re.IGNORECASE):
        book_info['language'] = 'French'
    else:
        book_info['language'] = 'English'

    return book_info

def extract_fields(image_path):
    raw_text = extract_text_easyocr(image_path)
    book_info = parse_book_info(raw_text)
    book_info["raw"] = raw_text
    return book_info

# ---------------------- ROUTES ---------------------- #
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/form', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        cert_path = generate_certificate(name)
        send_certificate_email(email, name, cert_path)
        return f"🎉 Certificate sent to {email}!"
    return render_template('form.html')

@app.route('/donate', methods=['GET','POST'])
def donate_combined():
    data = {}
    if request.method == 'POST':
        file = request.files['image']
        if file:
            save_dir = "static/images"
            os.makedirs(save_dir, exist_ok=True)
            path = os.path.join(save_dir, file.filename)
            file.save(path)

            # OCR + Genre Prediction
            data = extract_fields(path)
            if 'genre' not in data:
                data["genre"] = predict_genre(data.get("raw", ""))

            # Simulate updating request status
            donated_title = data.get("title", "").strip().lower()
            for req in request_list:
                if req["title"].strip().lower() == donated_title:
                    req["status"] = "Available"
                    req["action"] = "Buy"
                    break

    return render_template("donate.html", data=data)

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', user="Abhaya", requests=request_list)

@app.route('/booksearch')
def booksearch():
    return render_template('booksearch.html')

# ---------------------- START APP ---------------------- #
if __name__ == '__main__':
    app.run(debug=True)