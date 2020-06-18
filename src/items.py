from itertools import islice

from . import files
from . import properties
from . import utils
from . import randtools

r = randtools.r


class Item(files.Row, properties.PropsRowMixin):
    pass

class SuperItem(Item):
    pass

class UniqueItem(SuperItem):
    prop_types = {
        "normal": {
            "max_props": 12,
            "temps": ["prop{}", "par{}", "min{}", "max{}"]
        }
    }

    def get_lvl(self):
        return self.get("lvl req")

class SetMixin:
    def get_set_amounts(self):
        max_a = self.prop_types["set_a"]["max_props"]
        takes = r.randint(1, max_a)
        takes = min(takes, self.parts-1)
        amounts = {"set_a": takes}

        takes = r.randint(0, takes)
        amounts["set_b"] = takes
        return amounts

class SetItem(SuperItem, SetMixin):
    prop_types = {
        "normal": {
            "max_props": 9,
            "temps": ["prop{}", "par{}", "min{}", "max{}"]
        },
        "set_a": {
            "max_props": 5,
            "temps": ["aprop{}a", "apar{}a", "amin{}a", "amax{}a"]
        },
        "set_b": {
            "max_props": 5,
            "temps": ["aprop{}b", "apar{}b", "amin{}b", "amax{}b"]
        }
    }

    def __init__(self, idx, row, header):
        self.set_name = row[1]
        self.parts = self.set_numbers[self.set_name]
        super().__init__(idx, row, header)

    def get_prop_amounts(self):
        amounts = self.get_set_amounts()
        amounts["normal"] = r.randint(0, self.prop_types["normal"]["max_props"])
        return amounts

    def get_lvl(self):
        return self.get("lvl req")

class Set(SuperItem, SetMixin):
    FILE_NAME = "Sets"
    prop_types = {
        "set_a": {
            "max_props": 4,
            "temps": ["PCode{}a", "PParam{}a", "PMin{}a", "PMax{}a"],
            "first_prop_no": 2,
        },
        "set_b": {
            "max_props": 4,
            "temps": ["PCode{}b", "PParam{}b", "PMin{}b", "PMax{}b"],
            "first_prop_no": 2,
        },
        "set_full": {
            "max_props": 8,
            "temps": ["FCode{}", "FParam{}", "FMin{}", "FMax{}"]
        },
    }

    def __init__(self, idx, row, header):
        self.set_name = row[1]
        self.parts = self.set_numbers[self.set_name]
        super().__init__(idx, row, header)

    def get_lvl(self):
        return self.get("level")*1.5

    def get_prop_amounts(self):
        amounts = self.get_set_amounts()
        amounts["set_full"] = r.randint(0, self.prop_types["set_full"]["max_props"])
        return amounts

class RuneWord(SuperItem):
    FILE_NAME = "Runes"
    prop_types = {
        "normal": {
            "max_props": 7,
            "temps": ["T1Code{}", "T1Param{}", "T1Min{}", "T1Max{}"]
        }
    }

    def get_lvl(self):
        rune_cols = ["Rune{}".format(i) for i in range(1,7)]
        values = self.get_multiple(rune_cols)
        max_ = 0
        for val in values:
            try:
                val = int(val[1:])
                val = 3 + val * 2
                if max_ < val:
                    max_ = val
            except:
                pass
        return max_


class Rune(Item):
    FILE_NAME = "Gems"
    prop_types = {
        "weapon": {
           "max_props": 3,
           "temps": ["weaponMod{}Code", "weaponMod{}Param", "weaponMod{}Min", "weaponMod{}Max"]
        },
        "helm": {
           "max_props": 3,
           "temps": ["helmMod{}Code", "helmMod{}Param", "helmMod{}Min", "helmMod{}Max"]
        },
        "shield": {
           "max_props": 3,
           "temps": ["shieldMod{}Code", "shieldMod{}Param", "shieldMod{}Min", "shieldMod{}Max"]
        },
    }



class Items(files.Table, properties.PropsTableMixin):
    EXCLUDE = [
        lambda x: x[1] == ""
    ]

class SuperItems(Items):
    pass

class UniqueItems(SuperItems):
    entry_cls = UniqueItem
    FILE_NAME = "UniqueItems"
    EXCLUDE = Items.EXCLUDE + [
        "SuperKhalimFlail",
        lambda x: x[2] == ""
    ]

class SetItems(SuperItems):
    entry_cls = SetItem
    FILE_NAME = "SetItems"

    def make_set_numers(self):
        set_numbers = {}
        last_set = ""
        counter = 1
        for row in self.rows:
            current_set = row[1] 
            if current_set == last_set:
                counter += 1
            else:
                set_numbers[last_set] = counter
                counter = 1
            last_set = current_set
        set_numbers[last_set] = counter
        SetItem.set_numbers = set_numbers
        Set.set_numbers = set_numbers

    def make_entries(self):
        self.make_set_numers()
        super().make_entries()

class Sets(SuperItems):
    entry_cls = Set
    FILE_NAME = "Sets"


class RuneWords(SuperItems):
    entry_cls = RuneWord
    FILE_NAME = "Runes"
    EXCLUDE = Items.EXCLUDE + [
        lambda x: x[2] == "", 
    ]
    
class Runes(Items):
    entry_cls = Rune
    FILE_NAME = "Gems"
    # EXCLUDE = Items.EXCLUDE + [
    #     lambda x: "Rune" not in x, 
    # ]


class ItemRatio(files.Table):
    FILE_NAME = "ItemRatio"

    def increase_chances(self, m):
        cols = ["Unique", "Set", "UniqueMin", "SetMin"]
        for col in cols:
            self.divide_col(col, m, min_=1)


class Treasures(files.Table):
    FILE_NAME = "TreasureClassEx"

    def increase_rune_quantity(self, m):
        self.entry_map["Act 2 Good"].mul(["Prob4", "Prob5"], m)
        self.entry_map["Act 3 Good"].mul(["Prob4", "Prob5"], m)
        self.entry_map["Act 4 Good"].mul(["Prob5", "Prob6"], m)
        self.entry_map["Act 5 Good"].mul(["Prob6"], m)

        self.entry_map["Act 1 (N) Good"].mul(["Prob6"], m)
        self.entry_map["Act 2 (N) Good"].mul(["Prob6"], m)
        self.entry_map["Act 3 (N) Good"].mul(["Prob6"], m)
        self.entry_map["Act 4 (N) Good"].mul(["Prob6"], m)
        self.entry_map["Act 5 (N) Good"].mul(["Prob6"], m)

        self.entry_map["Act 1 (H) Good"].mul(["Prob6"], m)
        self.entry_map["Act 2 (H) Good"].mul(["Prob6"], m)
        self.entry_map["Act 3 (H) Good"].mul(["Prob6"], m)
        self.entry_map["Act 4 (H) Good"].mul(["Prob6"], m)
        self.entry_map["Act 5 (H) Good"].mul(["Prob6"], m)

    def increase_rune_quality(self, d):
        d = d * 10
        entries = [self.entry_map[key] for key in ["Runes {}".format(i) for i in range(2,17)]]
        self.divide_col("Prob3", d, min_=1, entries=entries)
        # for e in entries:
        #     e.calc(["Prob3"], lambda x: min(limit, x))
        self.entry_map["Runes 17"].calc(["Prob2"], lambda x: max(1, x/d))


        print("Changing highest possible rune drop for every act/difficulty")
        base_prop = self.entry_map["Act 2 (N) Good"].get("Prob6") // 2
        self.entry_map["Act 1 Good"].set_multiple(
            ["Item3", "Prob3", "Item4", "Prob4"],
            ["Runes 1", base_prop, "Runes 2", base_prop]
        )

        self.entry_map["Act 2 Good"].set_multiple(
            ["Item4", "Prob4", "Item5", "Prob5"],
            ["Runes 3", base_prop, "Runes 4", base_prop]
        )
        self.entry_map["Act 3 Good"].set_multiple(
            ["Item4", "Prob4", "Item5", "Prob5"],
            ["Runes 6", base_prop, "Runes 5", base_prop]
        )
        self.entry_map["Act 4 Good"].set_multiple(
            ["Item5", "Prob5", "Item6", "Prob6"],
            ["Runes 7", base_prop, "Runes 8", base_prop]
        )
        self.entry_map["Act 5 Good"].set_multiple(
            ["Item6", "Prob6", "Item7", "Prob7"],
            ["Runes 9", base_prop, "Runes 10", base_prop]
        )

        self.entry_map["Act 1 (N) Good"].set("Item6", "Runes 11")
        self.entry_map["Act 2 (N) Good"].set("Item6", "Runes 12")
        self.entry_map["Act 3 (N) Good"].set("Item6", "Runes 13")
        self.entry_map["Act 4 (N) Good"].set("Item6", "Runes 14")
        self.entry_map["Act 5 (N) Good"].set("Item6", "Runes 15")

        self.entry_map["Act 1 (H) Good"].set("Item6", "Runes 17")
        self.entry_map["Act 2 (H) Good"].set("Item6", "Runes 17")
        self.entry_map["Act 3 (H) Good"].set("Item6", "Runes 17")
        self.entry_map["Act 4 (H) Good"].set("Item6", "Runes 17")
        self.entry_map["Act 5 (H) Good"].set("Item6", "Runes 17")
