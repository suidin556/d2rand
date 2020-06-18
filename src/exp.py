from collections import defaultdict
from itertools import groupby

from . import files
from . import utils
from . import monsters
from . import randtools

r = randtools.r


class Level(files.Row):
    FILE_NAME = "Experience"


class Levels(files.Table):
    CLASS_COLS = ["Amazon", "Sorceress", "Necromancer", "Paladin", "Barbarian", "Druid", "Assassin"]
    FILE_NAME = "Experience"
    entry_cls = Level
    EXCLUDE = [
        {
            "Level": ["MaxLvl", "0"]
        }
    ]

    # def multiply_exp_ratios(self, m):
    #     self.multiply_col("ExpRatio", m, entries=entries)

    # def get_closest_base_divisor(self, d):
    #     if d < 5:
    #         return 2
    #     elif d < 10:
    #         return 5
    #     else:
    #         return 10


    def divide_required_exp(self, d):
        self.divide_col(self.CLASS_COLS, d, min_=1)

    # def randomize_exp_curve(self):
    #     group_len = 10
    #     for i in range(11, 92, group_len):
    #         entries = self.entries[i-group_len:i]
    #         exp_start = entries[0].get("Amazon")
    #         exp_end = entries[-1].get("Amazon")
    #         diff = exp_end - exp_start
    #         mid = diff // 2

    #         for entry in entries:
                

