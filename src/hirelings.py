from collections import defaultdict
from itertools import groupby

from . import files
from . import utils
from . import monsters
from . import randtools

r = randtools.r

merc_normal_stats = ["HP", "HP/Lvl", "Defense", "Def/Lvl", "Str", "Str/Lvl", "Dex", "Dex/Lvl", "AR", "AR/Lvl", ["Dmg-Min", "Dmg-Max"], "Dmg/Lvl", "Resist", "Resist/Lvl"]

class Merc(files.Row):
    FILE_NAME = "Hireling"


class Mercs(files.Table):
    FILE_NAME = "Hireling"
    entry_cls = Merc
    EXCLUDE = [
        {
            "Version": "0",
        }
    ]

    def randomize_and_adjust_stats(self):
        self.divide_col("Exp/Lvl", 3)

        mercs_by_act = groupby(self.entries, lambda x: x.get("Act"))
        for act, mercs in mercs_by_act:
            mercs = list(mercs)
            if act == 1:
                skill_col = "Skill2"
                for merc in mercs:
                    if merc.get("Difficulty") == 2:
                        if merc.get(skill_col) == "Cold Arrow":
                            merc.set(skill_col, "Ice Arrow")
                        elif merc.get(skill_col) == "Fire Arrow":
                            merc.set(skill_col, "Exploding Arrow")
                    elif merc.get("Difficulty") == 3:
                        if merc.get(skill_col) == "Cold Arrow":
                            merc.set(skill_col, "Freezing Arrow")
                        elif merc.get(skill_col) == "Fire Arrow":
                            merc.set(skill_col, "Immolation Arrow")
                adj = 1
            elif act == 2:
                adj = 0
            elif act == 3:
                self.multiply_col(["Level1", "Level2", "Level3"], 1.5, entries=mercs)
                adj = 1
            elif act == 5:
                adj = 0.5
            else:
                adj = 0
            for stat in merc_normal_stats:
                m = r.uniform(0.5 + adj, 2 + adj)
                self.multiply_col(stat, m, entries=mercs)

