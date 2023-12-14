import cv2
import numpy as np
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def image_threshold(image):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, image = cv2.threshold(image, 90, 255, cv2.THRESH_BINARY)

    return image

def text_in_image(image):
    image = image_threshold(image)
    text = pytesseract.image_to_string(image, lang="fra")

    return text