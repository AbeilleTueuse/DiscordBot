import cv2
import pytesseract
import time

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


class ReadMessage:
    KEY_WORDS = {
        "vaincu": "player_death",
        "mort": "player_death",
        "Schwarzy a été": "etchebest_invocation",
        "invoqué": "player_invocation",
        "feu": "fire_alight",
        "boss": "boss_begin",
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
                print("=" * 50, f"Text detected:", text, "=" * 50, sep="\n")
                return value