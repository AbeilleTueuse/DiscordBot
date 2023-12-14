import numpy as np

from PIL import ImageGrab

from event.detect_boss import BossDetection
from event.read_message import ReadMessage


class GameEvent:
    SCREEN_WIDTH, SCREEN_HEIGHT = ImageGrab.grab().size

    def __init__(self):
        self.bbox = self._calc_bbox()
        self.boss_detection = BossDetection()
        self.read_message = ReadMessage()

    def _calc_bbox(self):
        return (
            int(0.2 * self.SCREEN_WIDTH),
            int(0.8 * self.SCREEN_HEIGHT),
            int(0.9 * self.SCREEN_WIDTH),
            int(0.95 * self.SCREEN_HEIGHT),
        )
    
    def get_screen(self):
        image = ImageGrab.grab(bbox=self.bbox)
        return np.array(image)