import streamlit as st
from PIL import Image
from fpdf import FPDF  # fpdf2
import tempfile
import os
import re

# ----------------------
# Crop image horizontally into 3 equal vertical slices
# ----------------------
def crop_image_in_thirds_horizontal(img):
    w, h = img.size
    third_w = w // 3
    sets = [
        img.crop((0, 0, third_w, h)),              # Left third
        img.crop((third_w, 0, 2 * third_w, h)),    # Middle third
        img.crop((2 * third_w, 0, w, h))           # Right third
    ]
    return sets

# ----------------------
# Extract only variation lines from text
# ----------------------
def extract_variations(text):
    lines = text.splitlines()
    variations = []
    regex = r'^\s*[\d️⃣🪺🪹].*?/-.*$'  # matches numbered variation lines
    for line in lines:
        if re.match(regex, line.strip()):
            variations.append(line.strip())
    return variations

# ----------------------
# Save cropped ticket images to temp folder
# ----------------------
def save_images_temp(sets):
    paths = []
    for i, img in enumerate(sets):
        path = os.path.join(tempfile.gettempdir(), f"set_{i}.png")
        img.save(path)
        paths.append(path)
    return paths

# ----------------------
# PDF generation class (fpdf2)
# ----------------------
class PDF(FPDF):
    pass

def create_pdf(image_paths, variations, output_path):

    pdf = FPDF(format='A4')
    pdf.add_page()
    pdf.image(image_paths[0], x=5, y=10, w=100)    # Left half
    pdf.image(image_paths[1], x=110, y=10, w=100)  # Right half

    # --- Page 2: A3 portrait ---
    pdf.add_page()
    pdf.image(image_paths[2], x=5, y=10, w=100)   # Left side image

    # Move to right side for variations text
    pdf.set_xy(150, 20)
    pdf.set_font('Arial', '', 12)

    for var in variations:
        # Stripping non-latin-1 chars if font doesn't support emojis
        safe_line = var.encode('latin-1', 'ignore').decode('latin-1')
        pdf.multi_cell(0, 8, safe_line)

    pdf.output(output_path)

# ----------------------
# Streamlit App UI
# ----------------------
st.set_page_config(page_title="Tambola PDF Generator", layout="centered")
st.title("🎫 Tambola PDF Generator (Horizontal Image Split)")

st.write(
    "Upload a Tambola tickets image (containing 3 sets horizontally), paste the game text, "
    "and get your 2‑page PDF with tickets and variations."
)

uploaded_image = st.file_uploader("📷 Upload Tambola Tickets Image", type=['jpg', 'jpeg', 'png'])
text_message = st.text_area("📝 Paste the text message here", height=300)

if st.button("🚀 Generate PDF"):
    if uploaded_image and text_message.strip():
        with Image.open(uploaded_image) as img:
            sets = crop_image_in_thirds_horizontal(img)
            image_paths = save_images_temp(sets)
            variations = extract_variations(text_message)
            output_pdf = os.path.join(tempfile.gettempdir(), "tambola_output.pdf")
            create_pdf(image_paths, variations, output_pdf)
            with open(output_pdf, "rb") as f:
                st.download_button(
                    "📥 Download PDF",
                    f,
                    file_name="Tambola_Tickets.pdf",
                    mime="application/pdf"
                )
    else:
        st.warning("⚠ Please upload an image and paste your text message before generating the PDF.")
