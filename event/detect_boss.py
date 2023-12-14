import numpy as np
import os
import time

import cv2


class BossDetection:
    MARK_LEFT = cv2.cvtColor(cv2.imread(r"mark/left.png"), cv2.COLOR_BGR2GRAY)
    MARK_RIGHT = cv2.cvtColor(cv2.imread(r"mark/right.png"), cv2.COLOR_BGR2GRAY)

    UNIQUE_PIXEL_PATH = os.path.join("data", "unique_pixel.txt")
    UNIQUE_PIXEL = np.loadtxt(UNIQUE_PIXEL_PATH, dtype=int)

    MAX_TIME_WITHOUT_BOSS = 20

    def __init__(self):
        self.left_side = None
        self.right_side = None
        self.boss_is_alive = False
        self.timestamp = time.time()

    def detect_boss_bar_side(self, image, side: str):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        if side == "left":
            mark = self.MARK_LEFT
        else:
            mark = self.MARK_RIGHT
        res = cv2.matchTemplate(mark, image, cv2.TM_CCOEFF_NORMED)
        loc = np.where(res >= 0.95)
        coord = [pt for pt in zip(*loc)]
        if not len(coord):
            return False
        return coord[0]

    def is_boss_bar(self, image: np.ndarray):
        left_side = self.detect_boss_bar_side(image, side="left")
        if not left_side:
            return False
        right_side = self.detect_boss_bar_side(image, side="right")
        if not right_side:
            return False
        self.left_side = left_side
        self.right_side = right_side
        return True

    def _cut_to_bar(self, image: np.ndarray, left_side: tuple, right_side: tuple):
        image = image[
            left_side[0] + 10 : left_side[0] + 14,
            left_side[1] + self.MARK_LEFT.shape[1] : right_side[1],
        ]
        return image

    def _bar_threshold(self, image: np.ndarray):
        mask = np.zeros(image.shape[:2], dtype=bool)
        for color in self.UNIQUE_PIXEL:
            mask |= np.all(image == color, axis=2)
        return mask
    
    def calc_boss_hp_percentage(self, image: np.ndarray):
        if self.left_side is None or self.right_side is None:
            return
        
        image = self._cut_to_bar(image, self.left_side, self.right_side)
        image = self._bar_threshold(image)
        
        start_column = 0
        percent = 0
        min_pixel = image.shape[0]

        for next_column in np.linspace(0, image.shape[1], 101, dtype=int)[1:]:
            zone = image[:, start_column : next_column]

            if self.zone_is_hp(zone, min_pixel):
                percent += 1
                start_column = next_column
            else:
                return percent
            
        return percent

    def zone_is_hp(self, zone: np.ndarray, min_pixel: int):
        return zone.sum() >= min_pixel

    def unique_pixel(self, image: np.ndarray):
        unique = np.unique(image.reshape(-1, image.shape[2]), axis=0)
        np.savetxt(self.UNIQUE_PIXEL_PATH, unique, fmt="%d", delimiter="\t")

    def play_music(self, image: np.ndarray):
        if self.is_boss_bar(image):
            self.timestamp = time.time()
            
            if self.boss_is_alive:
                percentage = self.calc_boss_hp_percentage(image)

                if percentage == 0:
                    self.boss_is_alive = False
                    return True
                
            else:
                self.boss_is_alive = True
                return True
            
        else:
            if self.boss_is_alive:
                if time.time() - self.timestamp >= self.MAX_TIME_WITHOUT_BOSS:
                    self.boss_is_alive = False
                
        return False
