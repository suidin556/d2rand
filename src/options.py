import os
import sys
import json
import re
import time
from types import SimpleNamespace
from collections import OrderedDict

from . import utils

from . import APP_ROOT


option_dicts = [
    {
        "name": "FIXED_SEED",
        "desc": "Specify your seed as a positive integer. Otherwise current system time is used.",
        "type": int,
        "min": 0,
        "value": 1,
        "enabled": False,
        "group": "other",
    },
    {
        "name": "DIABLO_PATH",
        "desc": """
                    Path to put the generated data folder. Usually your Diablo II path.
                    Leave empty to use the current directory.
                """,
        "type": "directory",
        "enabled": True,
        "required": True,
        "group": "other",
    },
    {
        "name": "MIX_SUPER_PROPERTIES",
        "desc": """
                    Mixes properties of Uniques, Sets and Runewords.
                    This might change (and usually increase) the total number of properties.
                """,
        "type": bool,
        "group": "random",
        "enabled": True,
        "children": [
            {
                "name": "GROUP_BY_LEVEL",
                "desc": """
                            Puts all properties in 3 groups based on the level of the item they appear on.
                            Then mix them within those groups.
                        """,
                "type": bool,
                "enabled": False,
            },
        ],
    },
    {
        "name": "UNIQUE_DROP_MULTIPLIER",
        "desc": """
                    Increases the chance for Unique and Set Items.
                    Although it seems to mostly work for Uniques.
                """,
        "type": range,
        "min": 1,
        "max": 100,
        "group": "adjust",
        "enabled": False,
        "value": 5,
    },
    {
        "name": "MIX_MAGIC_PROPS",
        "desc": """
                    Mixes Prefix / Suffix properties.
                    Changes what props can be on what itemtypes, what props can be on the same item, as well as the level required for certain props. 
                """,
        "type": bool,
        "group": "random",
        "enabled": False,
        "children": [
            {
                "name": "GROUP_BY_LEVEL",
                "desc": """
                            Puts all properties in 3 groups based on the level of the item they appear on.
                            Then mix them within those groups.
                        """,
                "type": bool,
                "enabled": False,
            },
        ],
    },
    {
        "name": "MIX_MONSTER_LOCATIONS",
        "desc": "Mixes groups of monsters for each area. Bosses are excluded.",
        "group": "random",
        "type": bool,
        "enabled": False,
    },
    {
        "name": "MIX_MONSTER_STATS",
        "desc": "Mixes various monster stats. Right now only defensive stats and exp are mixed. Bosses are excluded.",
        "group": "random",
        "type": bool,
        "enabled": False,
    },
    {
        "name": "CHANGE_MONSTER_STATS",
        "desc": "Randomly multiplies monster stats by 0.5-2. Right now only defensive stats and exp are affected.",
        "group": "random",
        "type": bool,
        "enabled": False,
    },
    {
        "name": "RANDOM_AURAS",
        "desc": """Normal monsters have a chance to spawn with a random aura.
                   Resist auras are excluded because that seems annoying.
                """,
        "group": "random",
        "type": bool,
        "enabled": False,
    },
    {
        "name": "MIX_RUNE_PROPERTIES",
        "desc": """
                    Mixes Rune Properties.
                """,
        "group": "random",
        "type": bool,
        "enabled": True,
    },
    {
        "name": "EXPERIENCE_MULTIPLIER",
        "desc": """
                    Doesn't actually multiply the received exp,
                    but rather divides the required amount of exp for each level.
                """,
        "type": range,
        "group": "adjust",
        "min": 1,
        "max": 50,
        "enabled": False,
        "value": 10,
    },
    {
        "name": "INCREASE_MONSTER_DENSITY",
        "desc": """
                    Increases the monster density for all areas.
                """,
        "type": range,
        "group": "adjust",
        "min": 1,
        "max": 50,
        "enabled": False,
        "value": 1,
    },
    {
        "name": "INCREASE_RUNE_QUANTITY",
        "desc": """
                    Increases the chance of a rune drop,
                    but only if a rune drop was possible from that monster.
                    Does not increase the chance of getting a higher rune.
                """,
        "type": range,
        "min": 1,
        "max": 100,
        "group": "adjust",
        "enabled": False,
        "value": 10,
    },
    {
        "name": "INCREASE_RUNE_QUALITY",
        "desc": """
                    Increases the chance of getting higher runes.\n
                    This is logarithmic, meaning changing it from 1 to 10 increases it as much as changing it from 10 to 100\n
                    Also changes the highest possible rune droppable.\n
                    Normal up to Lem (based on Act), NM up to Ber (based on Act), Hell up to Zod (equal chance for all acts)
                """,
        "type": range,
        "group": "adjust",
        "min": 1,
        "max": 100,
        "enabled": False,
        "value": 2,
    },
    {
        "name": "GAMBLE_CHANCE_MULTIPLIER",
        "desc": """
                    Increases the gamble chance of sets an uniques.
                """,
        "type": range,
        "group": "adjust",
        "min": 1,
        "max": 100,
        "enabled": True,
        "value": 10,
    },
    {
        "name": "RANDOMIZE_MERC_STATS",
        "desc": """
                    Randomize some merc stats.
                    Also tries to rebalance mercs (so that act2 merc is not the the only option anymore).
                """,
        "group": "random",
        "type": bool,
        "enabled": False,
    },
    {
        "name": "FASTER_RUN_WALK",
        "desc": "Increases base walk and run speed of every character.",
        "group": "mode",
        "type": bool,
        "enabled": False,
    },
    {
        "name": "ADD_BASE_AR",
        "desc": "Every character will start out with a massive AR boost.",
        "group": "mode",
        "type": bool,
        "enabled": False,
    },
    {
        "name": "DEBUG",
        "desc": "If enabled no files will be written",
        "group": "other",
        "type": bool,
        "enabled": False,
    },
]

class OptionRequired(Exception):
    pass

class Option:
    def __init__(self, d):
        self.name = d["name"]
        self.desc = re.sub("(\s)\s+", "\g<1>", d["desc"].strip())
        self.type = d["type"]
        self.group = d.get("group")
        self.min = d.get("min")
        self.max = d.get("max")
        self._value = d.get("value")
        self.enabled = d.get("enabled")
        self.required = d.get("required", False)
        if self.required and not self.enabled:
            raise OptionRequired("The option {} is required, but was not supplied".format(self.name))

        children = d.get("children", [])
        self.options = Options(children)

    @property
    def value(self):
        return self._value

    def clean(self, val):
        if self.type in [range, int]:
            try:
                val = int(val)
            except ValueError:
                return val
            if self.min is not None:
                val = max(self.min, val)
            if self.max is not None:
                val = min(self.max, val)
        return val
    
    @value.setter
    def value(self, val):
        val = self.clean(val)
        self._value = val

    @property   
    def readable_name(self):
        parts = self.name.lower().split("_")
        parts = [p.capitalize() for p in parts]
        return " ".join(parts)



class Options(dict):
    def __init__(self, dicts):
        super().__init__()
        self.file_path = os.path.join(APP_ROOT, "last_settings.json")
        for d in dicts:
            self[d["name"]] = Option(d)

    def __getattr__(self, name):
        return self[name]

    def update_options(self, values):
        def rec(options, base_name=""):
            for name, o in options.items():
                if base_name:
                    name = "{}__{}".format(base_name, name)
                val = values.get(name, None)
                if val is None and o.required:
                    val = True
                if val is None:
                    continue
                o.enabled = val
                if o.type is not bool:
                    val_key = "{}__value".format(name)
                    val = values[val_key]
                    o.value = val
                rec(o.options, name)

        rec(self)

    def get_flat_dict(self):
        values = {}
        def rec(options, base_name=""):
            for name, o in options.items():
                if base_name:
                    name = "{}__{}".format(base_name, name)
                values[name] = o.enabled
                if o.type is not bool:
                    val_key = "{}__value".format(name)
                    values[val_key] = o.value
                rec(o.options, name)
                  
        rec(self)
        return values


    def save(self):
        flat_dict = self.get_flat_dict()
        with open(self.file_path, "w") as f:
            json.dump(flat_dict, f)

    def load(self):
        try:
            with open(self.file_path, "r") as f:
                data = json.load(f)
                self.update_options(data)
        except:
            pass

options = Options(option_dicts)
options.load()

def update_options(options, file_options, base=None):
    for name, option in options.items():
        if base is not None:
            name = "{}__{}".format(base, name)
        file_option = getattr(file_options, name, None)
        if file_option == name:
            option.enabled = True
            if option.type is not bool:
                option.value = file_option.val
            if option.options:
                update_options(option.options, file_options, name)
        else:
            option.enabled = False


def get_options_from_file():
    file_options = SimpleNamespace()
    with open(os.path.join(APP_ROOT, "options.txt")) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            
            split = line.split("=")
            attr = split[0].strip()
            if len(split) == 1:
                val = True
            else:
                val = split[1].strip()
                try:
                    val = float(val)
                    if int(val) == val:
                        val = int(val)
                except:
                    pass
            setattr(file_options, attr, val)
    return file_options


def update_options_from_file():
    file_options = get_options_from_file()
    update_options(options, file_options)
