#****Please don't forget the star**** 


#pip install --upgrade pip
#pip install opencv-python
#pip install numpy
#pip install pytesseract
#pip install Pillow

import cv2
import os
import numpy as np
import pytesseract
from PIL import Image

# Function to preprocess the image
def preprocess_image(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 5)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    return thresh

# Load the image #select name file image
img = cv2.imread("newspaper.jpg")

# Preprocess the image
preprocessed_img = preprocess_image(img)

# Find contours
contours, _ = cv2.findContours(preprocessed_img, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

# Find the columns in the image
column_boxes = []
for contour in contours:
    (x, y, w, h) = cv2.boundingRect(contour)
    aspect_ratio = w/h
    if aspect_ratio > 1.5 and w > 100 and h > 100:
        column_boxes.append((x, y, w, h))
column_boxes.sort()

# Process each column and save the text and image sections as separate files
for i, column in enumerate(column_boxes):
    x, y, w, h = column
    column_img = img[y:y+h, x:x+w]

    # Save any text sections as a JPG file
    text_boxes = []
    for contour in contours:
        (cx, cy, cw, ch) = cv2.boundingRect(contour)
        if x <= cx and cx <= x+w and y <= cy and cy <= y+h:
            aspect_ratio = cw/ch
            if 0.5 <= aspect_ratio <= 2:
                text_boxes.append((cx, cy, cw, ch))

    text_boxes.sort(key=lambda box: box[1])
    for j, box in enumerate(text_boxes):
        bx, by, bw, bh = box
        section_img = column_img[by:y+bh, bx:x+bw]
        text = pytesseract.image_to_string(section_img, lang="fas").strip()
        if text:
            file_path = f"column_{i}_section_{j}_text.jpg"
            Image.fromarray(section_img).save(file_path)

    # Save any image sections as a JPG file
    for j, contour in enumerate(contours):
        (cx, cy, cw, ch) = cv2.boundingRect(contour)
        if x <= cx and cx <= x+w and y <= cy and cy <= y+h:
            aspect_ratio = cw/ch
            if 0.5 <= aspect_ratio <= 2:
                section_img = column_img[cy:y+ch, cx:x+cw]
                section_gray = cv2.cvtColor(section_img, cv2.COLOR_BGR2GRAY)
                section_mean = np.mean(section_gray)
                if section_mean < 250:
                    file_path = f"column_{i}_section_{j}_image.jpg"
                    Image.fromarray(section_img).save(file_path)

# Move the original image file to a new directory to keep old newspapers
if not os.path.exists("old_newspapers"):
    os.mkdir("old_newspapers")
os.rename("newspaper.jpg", "old_newspapers/newspaper.jpg")
    
