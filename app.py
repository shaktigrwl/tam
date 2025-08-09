import streamlit as st
from PIL import Image
from fpdf import FPDF
import tempfile
import re
import os

def crop_image_in_thirds(img):
    w, h = img.size
    third = h // 3
    sets = [
        img.crop((0, 0, w, third)),                  # Top third
        img.crop((0, third, w, 2*third)),            # Middle third
        img.crop((0, 2*third, w, h))                 # Bottom third
    ]
    return sets

def extract_variations(text):
    lines = text.split('\n')
    variations = []
    regex = r'^[\d️⃣🪺🪹].*?/-.*$'
    for line in lines:
        if re.match(regex, line.strip()):
            variations.append(line.strip())
    return variations

def save_images_temp(sets):
    paths = []
    for i, img in enumerate(sets):
        path = tempfile.gettempdir() + f"/set_{i}.png"
        img.save(path)
        paths.append(path)
    return paths

def create_pdf(image_paths, variations, output_path):
    pdf = FPDF(unit='mm', format='A4')
    pdf.add_page()
    # Page 1: A4
    pdf.image(image_paths[0], x=5, y=10, w=100)
    pdf.image(image_paths[1], x=110, y=10, w=100)
    # Page 2: A3
    pdf.add_page()    
    pdf.image(image_paths[2], x=10, y=10, w=130)
    pdf.set_xy(150, 20)
    pdf.set_font('Arial', '', 12)
    for var in variations:
        safe_line = var.encode('latin-1', 'ignore').decode('latin-1')
        pdf.multi_cell(0, 8, safe_line)
    pdf.output(output_path)
    return output_path

st.title("Tambola PDF Generator App")

uploaded_image = st.file_uploader("Upload Tambola Tickets Image (JPG/PNG)", type=['jpg', 'png'])
text_message = st.text_area("Paste the text message here", height=300)

if st.button("Generate PDF"):
    if uploaded_image is not None and text_message:
        with Image.open(uploaded_image) as img:
            sets = crop_image_in_thirds(img)
            image_paths = save_images_temp(sets)
            variations = extract_variations(text_message)
            output_pdf = tempfile.gettempdir() + "/tambola_output.pdf"
            create_pdf(image_paths, variations, output_pdf)
            with open(output_pdf, "rb") as f:
                st.download_button("Download PDF", f, "Tambola_Tickets.pdf", mime="application/pdf")
    else:
        st.warning("Please upload an image and paste your text message.")

