from collections import defaultdict

from . import files
from . import utils
from . import monsters
from . import randtools

r = randtools.r



class MonsterLvls(files.Row):
    FILE_NAME = "MonLvl"

class MonsterStats(files.Row):
    FILE_NAME = "MonStats"



class Levels(files.Table):
    FILE_NAME = "Levels"
    EXCLUDE = [
        {
            "mon1": "",
            "QuestFlag": "26",
            # "MonDen": "0",
            "Id": "",
            "Name": ["Act 5 - Mountain Top", "Act 5 - Temple Entrance"]
        }
    ]

    def add_monster_density(self, value):
        siege_mon_den = self.entry_map["Act 5 - Siege 1"].get("MonDen")
        self.entry_map["Act 5 - Siege 1"].set("MonDen", siege_mon_den)
        value = value * 100
        cols = ["MonDen", "MonDen(N)", "MonDen(H)"]
        self.add_col(cols, value)

    def mix_all_monster_locations(self):
        siege_mon_den = self.entry_map["Act 5 - Siege 1"].get("MonDen")
        self.entry_map["Act 5 - Siege 1"].set("MonDen", siege_mon_den)

        monster_cols_normal = ["mon{}".format(i) for i in range(1,11)]
        monster_cols_nightmare = ["nmon{}".format(i) for i in range(1,11)]

        levels = self.sort_by_col("MonLvl1Ex")

        self.mix_monster_locations(monster_cols_normal, levels, 3)
        self.mix_monster_locations(monster_cols_nightmare, levels, 2)


    def mix_monster_locations(self, monster_cols, levels, radius_divisor): 
        max_mons = 10
        start = 1
        end = len(levels)

        for idx in range(start, end):
            level = levels[idx]
            min_idx, max_idx = utils.get_idx_interval(idx, max(start, idx-20), end, radius_divisor)

            group = levels[min_idx:max_idx]
            monsters_for_level = utils.flatten(self.get_cols_values(monster_cols, group))
            monsters_for_level = set(monsters_for_level)
            try:
                monsters_for_level.remove("")
            except KeyError:
                pass

            choose_new = min(len(monsters_for_level), max_mons)

            monsters = r.sample(monsters_for_level, choose_new)

            level.set_multiple(monster_cols, monsters)
            # level.set("NumMon", len(monsters)//2+1)

class DifficultyLevels(files.Table):
    FILE_NAME = "DifficultyLevels"
    
    def multiply_gamble_chance(self, m):
        m *= 5
        self.multiply_col("GambleSet", m)
        self.multiply_col("GambleUnique", m)
