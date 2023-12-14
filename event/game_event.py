import numpy as np

from PIL import ImageGrab


class GameEvent:
    SCREEN_WIDTH, SCREEN_HEIGHT = ImageGrab.grab().size

    def __init__(self):
        self.bbox = self._calc_bbox()

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


if __name__ == "__main__":
    game_event = GameEvent()
    print(game_event.get_screen())