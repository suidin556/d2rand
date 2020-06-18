import time

from . import files
from . import items
from . import magic
from . import monsters
from . import chars
from . import levels
from . import hirelings
from . import exp
from . import properties

from . import randtools
from .options import options


def do():
    files.clear_out_files()

    seed_o = options.FIXED_SEED
    if seed_o.enabled:
        seed = seed_o.value
    else:
        seed = int(time.time())
    randtools.r.seed(seed)
    print("Starting Randomizer with seed: {}".format(seed))
    options.save()
    
    randomize_items()
    randomize_magic()
    randomize_monsters()
    randomize_levels()
    randomize_mercs()
    randomize_exp()
    randomize_chars()

    print("Randomization done. Copying data folder...")
    d2path = options.DIABLO_PATH.value
    try:
        files.copy_data_dir(d2path)
    except Exception as e:
        print("ERROR. Could not copy the data dir to {}.".format(d2path))
    else:
        print("Successfully copied data dir to {}.".format(d2path))

def mix_props(mix_types, group_by_lvl=True):
    mixer = properties.RndPropsPool(mix_types)
    if group_by_lvl:
        mixer.redistribute_by_lvl()
    else:
        mixer.redistribute()
    mixer.write()


def randomize_items():
    if options.MIX_SUPER_PROPERTIES.enabled:
        print("Mixing Unique/Set/Runeword properties")
        mix_types = [
            items.UniqueItems(),
            items.SetItems(),
            items.Sets(),
            items.RuneWords(),
        ]
        mix_props(mix_types, options.MIX_SUPER_PROPERTIES.options.GROUP_BY_LEVEL.enabled)


    if options.MIX_RUNE_PROPERTIES.enabled:
        print("Mixing Rune Properties")
        i = items.Runes()
        i.mix_props()


    if options.UNIQUE_DROP_MULTIPLIER.enabled:
        print("Increasing Unique and Set drop chance.")
        i = items.ItemRatio()
        i.increase_chances(options.UNIQUE_DROP_MULTIPLIER.value)
        i.write()

    t = False

    if options.INCREASE_RUNE_QUANTITY.enabled:
        t = items.Treasures()
        print("Increasing Rune drop chance.")
        t.increase_rune_quantity(options.INCREASE_RUNE_QUANTITY.value)

    if options.INCREASE_RUNE_QUALITY.enabled:
        t = t or items.Treasures()
        print("Limiting Rune downgrade chance.")
        t.increase_rune_quality(options.INCREASE_RUNE_QUALITY.value)

    if t:
        t.write()

def randomize_magic():
    if options.MIX_MAGIC_PROPS.enabled:
        print("Mixing Magic Prefixes/Suffixes")
        mix_types = [
            magic.MagicPrefixes(),
            magic.MagicSuffixes(),
        ]
        mix_props(mix_types, options.MIX_SUPER_PROPERTIES.options.GROUP_BY_LEVEL.enabled)

def randomize_monsters():

    ms = False
    if options.MIX_MONSTER_STATS.enabled:
        print("Mixing Monster Stats")
        ms = monsters.MonstersStats()
        ms.mix_monster_stats()

    if options.CHANGE_MONSTER_STATS.enabled:
        print("Changing Monster Stats")
        ms = ms or monsters.MonstersStats()
        ms.alter_monster_stats()

    if options.RANDOM_AURAS.enabled:
        ms = ms or monsters.MonstersStats()
        ms.set_mon_prop_ids()
    if ms:
        ms.write()

    mp = monsters.MonsterProps()
    if options.RANDOM_AURAS.enabled:
        print("Creating random auras on monsters")
        mp = mp or monsters.MonsterProps()
        mp.create_rnd_auras()

    if mp:
        mp.write()



def randomize_levels():
    l = False
    if options.MIX_MONSTER_LOCATIONS.enabled:
        print("Mixing Monster Locations")
        l = levels.Levels()
        l.mix_monsters_in_areas()
    if options.INCREASE_MONSTER_DENSITY.enabled:
        print("Increasing monster density")
        l = l or levels.Levels()
        l.add_monster_density(options.INCREASE_MONSTER_DENSITY.value)
    if l:
        l.write()

    if options.GAMBLE_CHANCE_MULTIPLIER.enabled:
        print("Increasing Unique and Set gamble chances")
        diff = levels.DifficultyLevels()
        diff.multiply_gamble_chance(options.GAMBLE_CHANCE_MULTIPLIER.value)
        diff.write()

def randomize_mercs():
    if options.RANDOMIZE_MERC_STATS.enabled:
        print("Randomizing Mercenaries stats")
        m = hirelings.Mercs()
        m.randomize_and_adjust_stats()
        m.write()


def randomize_exp():

    levels = False
    if options.EXPERIENCE_MULTIPLIER.enabled:
        print("Reducing the required exp by a factor of".format(options.EXPERIENCE_MULTIPLIER.value))
        levels = exp.Levels()
        levels.divide_required_exp(options.EXPERIENCE_MULTIPLIER.value)
    if levels:
        levels.write()

def randomize_chars():
    c = False
    if options.ADD_BASE_AR.enabled:
        print("Adding base AR to every character")
        c = chars.Chars()
        c.to_hit_factor(100000)
    if options.FASTER_RUN_WALK.enabled:
        print("Increasing base walk and run speed of every character.")
        c = c or chars.Chars()
        c.set_walk_run(11, 14)
    if c:
        c.write()
