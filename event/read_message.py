import cv2
import numpy as np
import pytesseract
import time

pytesseract.pytesseract.tesseract_cmd = r"C:\Users\admin\miniconda3\envs\discord\Library\bin\tesseract.exe"

def image_threshold(image):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, image = cv2.threshold(image, 90, 255, cv2.THRESH_BINARY)

    return image

def text_in_image(image):
    image = image_threshold(image)
    text = pytesseract.image_to_string(image, lang="fra", config=r"--tessdata-dir C:\Users\admin\miniconda3\envs\discord\Library\bin")

    return text

img = cv2.imread(r"reference\test.png")
t1 = time.time()
text = text_in_image(img)
t2 = time.time()
print(t2-t1)
print(text)