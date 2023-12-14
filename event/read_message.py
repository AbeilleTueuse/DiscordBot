import cv2
import pytesseract
import time

pytesseract.pytesseract.tesseract_cmd = r"C:\Users\admin\miniconda3\envs\discord\Library\bin\tesseract.exe"


class ReadMessage:
    KEY_WORDS = {
        "vaincu": "player_death",
        "mort": "player_death",
        "invoqué": "player_inovcation",
        "feu": "fire_alight"
    }.items()

    TIME_BETWEEN_MESSAGE = 8

    def __init__(self):
        self.last_timestamp = time.time()

    def image_threshold(self, image):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, image = cv2.threshold(image, 90, 255, cv2.THRESH_BINARY)

        return image

    def image_to_text(self, image):
        image = self.image_threshold(image)
        text = pytesseract.image_to_string(image, lang="fra")

        return text
    
    def image_to_game_event(self, image):
        if time.time() - self.last_timestamp <= self.TIME_BETWEEN_MESSAGE:
            return
        
        text = self.image_to_text(image)

        for key, value in self.KEY_WORDS:
            if key in text:
                self.last_timestamp = time.time()
                return value
        

if __name__ == "__main__":
    read_message = ReadMessage()
    img = cv2.imread(r"reference\test2.png")
    print(read_message.image_to_game_event(img))