from . import skills

PROPERTY_GROUPS = [
    {
        "codes": ["ama", "ass", "bar", "dru", "nec", "pal", "sor", "allskills", "fireskill"],
        "values": {
            "min": [1, 3], "max": [2, 5],
        }
    },
    {
        "codes": ["skill"],
        "values": {
            "min": [1, 5], "max": [3, 7],
            "param": lambda: skills.get_rnd_skill_id()
        }
    },
    {
        "codes": ["oskill"],
        "values": {
            "min": [3, 7], "max": [7, 20],
            "param": lambda: skills.get_rnd_skill_name()
        }
    },
    {
        "codes": ["skilltab"],
        "values": {
            "min": [2, 4], "max": [3, 5],
            "param": lambda: skills.get_rnd_skilltab_id()
        }
    },
    {
        "codes": ["att-skill", "hit-skill", "gethit-skill"],
        "values": {
            "min": [5, 35], "max": [5, 30],
            "param": lambda: skills.get_rnd_skill_id(restrict="usable")
        }
    },
    {
        "codes": ["kill-skill"],
        "values": {
            "min": [10, 60], "max": [10, 40],
            "param": lambda: skills.get_rnd_skill_id(restrict="usable")
        }
    },
    {
        "codes": ["death-skill", "levelup-skill"],
        "values": {
            "min": 100, "max": [20, 50],
            "param": lambda: skills.get_rnd_skill_id(restrict="usable")
        }
    },
    {
        "codes": ["charged"],
        "values": {
            "min": [5, 50], "max": [5, 30],
            "param": lambda: skills.get_rnd_skill_id(restrict="usable")
        }
    },
    {
        "codes": ["aura"],
        "values": {
            "min": [5, 8], "max": [10, 20],
            "param": lambda: skills.get_rnd_skill_id(restrict="aura")
        }
    },
    {
        "codes": ["thorns", "light-thorns"],
        "values": {
            "min": [10, 20], "max": [20, 250],
        }
    },
    {
        "codes": ["sock"],
        "values": {
            "param": lambda: r.randint(1,6)
        }
    },
    {
        "codes": ["str/lvl", "dex/lvl", "enr/lvl", "vit/lvl"],
        "values": {
            "param": lambda: r.randint(4,16)
        }
    },
]
