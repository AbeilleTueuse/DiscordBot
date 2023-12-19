import numpy as np
import os
import json

from PIL import ImageGrab
import pandas as pd
import regex as re

from event.detect_boss import BossDetection
from event.read_message import ReadMessage


class GameEvent:
    SCREEN_WIDTH, SCREEN_HEIGHT = ImageGrab.grab().size
    EVENT_GLOBAL_PATH = os.path.join("event", "event_global.json")
    EVENT_PER_PSEUDO_PATH = os.path.join("event", "event_per_pseudo.txt")
    DEFAULT_EVENT_SOUND = {
        "invocation": "random",
        "death": "il_est_decede",
        }
    EVENT_TO_FRENCH = {
        "invocation": "Invocation",
        "death": "Mort",
        "fire": "Feu",
        "boss": "Boss"
    }
    FRENCH_TO_EVENT = {value: key for key, value in EVENT_TO_FRENCH.items()}

    BOSS_REGEX = r"boss_(\d+)"
    BOSS_DISPLAY = "Boss {} %"

    def __init__(self):
        self.bbox = self._calc_bbox()
        self.event_global = self._get_event_global()
        self.event_per_pseudo = self._get_event_per_pseudo()
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

    def _get_event_global(self) -> dict:
        with open(self.EVENT_GLOBAL_PATH, "r") as file:
            return json.load(file)
        
    def _get_event_per_pseudo(self):
        return pd.read_csv(self.EVENT_PER_PSEUDO_PATH, header=0, index_col=[0])

    def _save_event_global(self):
        with open(self.EVENT_GLOBAL_PATH, "w") as file:
            json.dump(self.event_global, file, indent=4)

    def _save_event_per_pseudo(self):
        self.event_per_pseudo.to_csv(self.EVENT_PER_PSEUDO_PATH)

    def is_new_pseudo(self, pseudo: str):
        return pseudo not in self.event_per_pseudo.index

    def add_pseudo(self, pseudo: str):
        self.event_per_pseudo.loc[pseudo] = self.DEFAULT_EVENT_SOUND
        self._save_event_per_pseudo()

    def delete_pseudo(self, pseudo: str):
        self.event_per_pseudo.drop(pseudo, inplace=True)
        self._save_event_per_pseudo()

    def translate_event(self, event_name: str):        
        if event_name in self.EVENT_TO_FRENCH:
            return self.EVENT_TO_FRENCH[event_name]
        
        return event_name
    
    def translate_global_event(self, event_name: str):
        match = re.match(self.BOSS_REGEX, event_name)
        if match:
            return self.BOSS_DISPLAY.format(match.group(1))
        return self.translate_event(event_name)
    
    def untranslate_event(self, event: str):
        if event in self.FRENCH_TO_EVENT:
            return self.FRENCH_TO_EVENT[event]
        return event
    
    def exists(self, event: str):
        return event in self.event_per_pseudo.columns
    
    def change_event(self, pseudo, event: str, sound: str):
        self.event_per_pseudo.loc[pseudo, event] = sound
        self._save_event_per_pseudo()


if __name__ == "__main__":
    game_event = GameEvent()
    print(game_event.display_per_player())
