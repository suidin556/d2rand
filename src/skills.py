from . import files
from . import randtools

r = randtools.r




class Skill(files.Row):
    FILE_NAME = "Skills"
    pass

class Skills(files.Table):
    EXCLUDE = [
        lambda x: x[2] == ""
    ]
    entry_cls = Skill
    FILE_NAME = "Skills"

    def get_skills_col(self, col, restrict=False):
        vals = []
        for entry in self.entries:
            if restrict == "usable":
                if entry.get("passivestate") != "":
                    continue
            elif restrict == "aura":
                if not entry.get("aura"):
                    continue
            vals.append(entry.get(col))
        return vals


skills = Skills()
def get_rnd_skill_id(restrict=False):
    return r.choice(skills.get_skills_col("Id", restrict))

def get_rnd_skill_name(restrict=False):
    return r.choice(skills.get_skills_col("skill", restrict))
    
