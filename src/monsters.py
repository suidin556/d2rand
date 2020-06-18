from collections import defaultdict

from . import files
from . import utils
from . import randtools
from . import properties

r = randtools.r



class MonsterLvls(files.Row):
    FILE_NAME = "MonLvl"

class MonsterStats(files.Row):
    FILE_NAME = "MonStats"





class MonsterProp(files.Row, properties.PropsRowMixin):
    prop_types = {
        "normal": {
            "max_props": 6,
            "temps": ["prop{}", "chance{}", "par{}", "min{}", "max{}"]
        },
        "nightmare": {
            "max_props": 6,
            "temps": ["prop{} (N)", "chance{} (N)", "par{} (N)", "min{} (N)", "max{} (N)"]
        },
        "hell": {
            "max_props": 6,
            "temps": ["prop{} (H)", "chance{} (H)", "par{} (H)", "min{} (H)", "max{} (H)"]
        }
    }
    FILE_NAME = "MonProp"



class MonstersLvls(files.Table):
    entry_cls = MonsterLvls
    FILE_NAME = "MonLvl"

class MonstersStats(files.Table):
    entry_cls = MonsterStats
    FILE_NAME = "MonStats"

    EXCLUDE = [
        {
            "boss": "1",
            "npc": "1",
            "enabled": "",
            "inTown": "1",
            "NameStr": ["unused", "Dummy", "a trap", "", "Turret", "Hydra"],
            "AI": ["Idle", "Ancient"],
            "MonType": "construct",
            "Align": "1",
            "killable": "",
            "Level": "",
        },
    ]

    STATS = [
        "minHP",
        "MinHP(N)",
        "MinHP(H)",
        "maxHP",
        "MaxHP(N)",
        "MaxHP(H)",
        "AC",
        "Exp", 
    ] + utils.flatten(
        [utils.diff_col_names(col) for col in [
            "ResDm", "ResMa", "ResFi", "ResLi", "ResCo", "ResPo",
            "AC", "Exp"
        ]])

    def mix_monster_stats(self):
        # groups = self.group_by_col("Level", 10)
        # for group in groups:
        #     stat_groups = self.get_stats()
        #     for stats in stat_groups:
        #         self.mix_cols(stats, group)

        monsters = self.sort_by_col("Level")

        start = 5
        end = len(monsters)

        for idx in range(start, end):
            monster = monsters[idx]
            min_idx, max_idx = utils.get_idx_interval(idx, start, end)

            group = set(monsters[min_idx:max_idx])
            group.remove(monster)
            group = list(group)

            switch_with = r.choice(group)
            self.switch_cols(self.STATS, monster, switch_with)


    def alter_monster_stats(self):
        for e in self.entries:
            m = r.uniform(0.5, 2)
            for col in self.STATS:
                val = e.get(col)
                if val == "":
                    continue
                val = m * val
                e.set(col, val)

    def set_mon_prop_ids(self):
        for mon in self.entries:
            mon.set("MonProp", mon.get("Id"))

    def merc_stats(self):
        A1 = 271
        A2 = 338
        A3 = 359
        A5 = 561

monstats_base = MonstersStats()


class MonsterProps(files.Table, properties.PropsTableMixin):
    EXCLUDE = [
    ]
    entry_cls = MonsterProp
    FILE_NAME = "MonProp"

    def create_rnd_auras(self):
        vanilla_mons_with_props = utils.flatten(self.get_cols_values("Id"))
        monsters = monstats_base.entries
        pgen = properties.PropGen("aura", params=[98, 99, 104, 108, 109, 113, 114, 115, 118, 120, 122, 123, 124])
        lvl_cols = {"normal": "Level", "nightmare": "Level(N)", "hell": "Level(H)"}
        diff_chances = {"normal": 5, "nightmare": 10, "hell": 15}

        for monster in monsters:
            mon_name = monster.get("Id")
            if mon_name in vanilla_mons_with_props:
                continue
            entry = self.append_entry()
            entry.set("Id", mon_name)
            for type_ in self.entry_cls.prop_types.keys():
                lvl = monster.get(lvl_cols[type_])

                min_ = max(1, lvl // 4)
                max_ = min_ + max(1, min_ // 2)

                chance = diff_chances[type_]

                p = pgen.gen_prop(min_, max_, chance)
                entry.overwrite(type_, p)


