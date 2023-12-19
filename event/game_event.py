import numpy as np
import os
import json

from PIL import ImageGrab

from event.detect_boss import BossDetection
from event.read_message import ReadMessage


class GameEvent:
    SCREEN_WIDTH, SCREEN_HEIGHT = ImageGrab.grab().size
    EVENT_PATH = os.path.join("event", "event.json")

    def __init__(self):
        self.bbox = self._calc_bbox()
        self.data = self._open_json()
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

    def _open_json(self) -> list:
        with open(self.EVENT_PATH, "r") as file:
            return json.load(file)

    def _save_json(self):
        with open(self.EVENT_PATH, "w") as file:
            json.dump(self.data, file, indent=4)

    def get_event_per_pseudo(self) -> dict:
        return self.data["per_pseudo"]

    def pseudo_is_added(self, pseudo: str):
        return pseudo in self.get_event_per_pseudo()

    def add_pseudo(self, pseudo: str):
        self.get_event_per_pseudo()[pseudo] = self._default_pseudo_event()
        self._save_json()

    def delete_pseudo(self, pseudo: str):
        del self.get_event_per_pseudo()[pseudo]
        self._save_json()

    def _default_pseudo_event(self):
        return {"invocation": "random", "mort": "il_est_decede"}