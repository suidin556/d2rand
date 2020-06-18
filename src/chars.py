from . import files
from . import utils
from . import randtools




class Char(files.Row):
    FILE_NAME = "CharStats"


class Chars(files.Table):
    FILE_NAME = "CharStats"
    entry_cls = Char
    EXCLUDE = [
        {
            "str": "",
        }
    ]

    def to_hit_factor(self, amount=500):
        self.add_col("ToHitFactor", amount)

    def to_walk_run(self, walk, run=None):
        if run is None:
            run = walk
        self.add_col("WalkVelocity", walk, 1, 5)
        self.add_col("RunVelocity", run, 1, 5)

    def set_walk_run(self, walk, run=None):
        if run is None:
            run = walk
        self.set_col("WalkVelocity", walk)
        self.set_col("RunVelocity", run)
