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

    def mix_monsters_in_areas(self):

        siege_mon_den = self.entry_map["Act 5 - Siege 1"].get("MonDen")
        self.entry_map["Act 5 - Siege 1"].set("MonDen", siege_mon_den)

        monster_cols_normal = ["mon{}".format(i) for i in range(1,11)]
        monster_cols_nightmare = ["nmon{}".format(i) for i in range(1,11)]
        monster_cols = monster_cols_normal + monster_cols_nightmare

        levels = self.sort_by_col("MonLvl1Ex")
        
        max_mons = 10

        start = 1
        end = len(levels)


        used_monsters = set()
        for idx in range(start, end):
            level = levels[idx]
            min_idx, max_idx = utils.get_idx_interval(idx, max(start, idx-20), end)

            group = levels[min_idx:max_idx]
            monsters_for_level = utils.flatten(self.get_cols_values(monster_cols, group))
            monsters_for_level = set(monsters_for_level)
            try:
                monsters_for_level.remove("")
            except KeyError:
                pass

            monsters_for_level = set(monsters_for_level) - used_monsters
            choose_new = min(len(monsters_for_level), max_mons)

            monsters = set(r.sample(monsters_for_level, choose_new))
            l_new = len(monsters)
            if l_new < max_mons:
                l_used = len(used_monsters)
                choose_old = min(l_used, max_mons-l_new)
                if choose_old:
                    old_monsters = r.sample(used_monsters, choose_old)
                    monsters |= set(old_monsters)

            used_monsters |= monsters

            for m, col in zip(monsters, monster_cols_normal):
                level.set(col, m)
            for m, col in zip(monsters, monster_cols_nightmare):
                level.set(col, m)
            level.set("NumMon", len(monsters)//2+1)

class DifficultyLevels(files.Table):
    FILE_NAME = "DifficultyLevels"
    
    def multiply_gamble_chance(self, m):
        m *= 5
        self.multiply_col("GambleSet", m)
        self.multiply_col("GambleUnique", m)
