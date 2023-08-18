import streamlit as st
import cv2
import numpy as np
import easyocr
import mysql.connector
import sqlite3


# Set up the Streamlit app title and layout
st.title("Business Card OCR")
st.sidebar.header("Upload Image")
st.set_option('deprecation.showfileUploaderEncoding', False)

# Create SQLite database and table if they don't exist
conn = sqlite3.connect("business_card.db")
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS cards
          (id INTEGER PRIMARY KEY AUTOINCREMENT,
          name TEXT,
          phone TEXT,
          email TEXT,
          company TEXT,
          image BLOB)''')

# Function to perform OCR on the uploaded image
def perform_ocr(image):
    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply image processing techniques (e.g., resizing, cropping, thresholding) to enhance image quality
    resized = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    blurred = cv2.GaussianBlur(resized, (5, 5), 0)
    _, thresholded = cv2.threshold(blurred, 100, 255, cv2.THRESH_BINARY)

    # Perform OCR on the enhanced image
    reader = easyocr.Reader(['en'])  # Specify the language(s) for OCR
    result = reader.readtext(thresholded)
    return result

# Function to insert data into the database
def insert_data(name, phone, email, company, image):
    conn = sqlite3.connect("business_card.db")
    c = conn.cursor()
    c.execute("INSERT INTO cards (name, phone, email, company, image) VALUES (?, ?, ?, ?, ?)",
              (name, phone, email, company, image))
    conn.commit()
    conn.close()

# Streamlit app main content
uploaded_file = st.sidebar.file_uploader("Choose an image", type=["jpg", "jpeg", "png"])
if uploaded_file is not None:
    image = cv2.imdecode(np.fromstring(uploaded_file.read(), np.uint8), 1)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    

    # Display the uploaded image
    st.sidebar.image(image, caption='Uploaded Image', use_column_width=True)

    # Perform OCR when the "Extract Text" button is clicked
    if st.sidebar.button('Extract Text'):
        ocr_result = perform_ocr(image)
        extracted_text = [text[1] for text in ocr_result]

        # Display the extracted information
        st.subheader("Extracted Information")
        for text in extracted_text:
            st.write(text)

        # Save extracted information to the database when the "Save Data" button is clicked
        if st.button("Save Data"):
            name = st.text_input("Name")
            phone = st.text_input("Phone")
            email = st.text_input("Email")
            company = st.text_input("Company")

            if name and phone and email and company:
                insert_data(name, phone, email, company, uploaded_file.read())
                st.success("Data saved successfully!")

# Allow the user to view and delete data from the database
if st.checkbox("View Saved Data"):
    conn = sqlite3.connect("business_card.db")
    c = conn.cursor()
    c.execute("SELECT * FROM cards")
    data = c.fetchall()

    if data:
        st.subheader("Saved Data")
        for card in data:
            card_id, name, phone, email, company, _ = card
            st.write(f"Card ID: {card_id}")
            st.write(f"Name: {name}")
            st.write(f"Phone: {phone}")
            st.write(f"Email: {email}")
            st.write(f"Company: {company}")
            

        
           
