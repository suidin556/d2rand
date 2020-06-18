
from . import files
from . import utils
from . import randtools
from . import properties

r = randtools.r




class MagicAttr(files.Row, properties.PropsRowMixin):
    prop_types = {
        "normal": {
            "max_props": 3,
            "temps": ["mod{}code", "mod{}param", "mod{}min", "mod{}max"]
        }
    }
    def get_lvl(self):
        return self.get("levelreq") or 1

    def apply_props(self, prop_iter):
        for prop_type in self.prop_types.keys():
            takes = 2 if randtools.chance(10) else 1
            self.apply_to_props_type(prop_type, prop_iter, takes=takes)

class MagicPrefix(MagicAttr):
    pass

class MagicSuffix(MagicAttr):
    pass

class MagicAttrs(files.Table, properties.PropsTableMixin):
    EXCLUDE = [
        lambda x: x[1] == "",
        lambda x: x[4] == ""
    ]

class MagicPrefixes(MagicAttrs):
    entry_cls = MagicPrefix
    FILE_NAME = "MagicPrefix"

class MagicSuffixes(MagicAttrs):
    entry_cls = MagicSuffix
    FILE_NAME = "MagicSuffix"


