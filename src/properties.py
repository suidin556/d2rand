from dataclasses import dataclass
from collections.abc import Iterable
from itertools import islice, groupby

from . import utils
from .options import options
from . import randtools
from . import proptypes

r = randtools.r

@dataclass(eq=False)
class Prop:
    code: str
    param: str
    min: str
    max: str
    lvl: int = 1
    chance: int = None

    def as_list(self):
        chance = self.chance
        if chance is None:
            return [self.code, self.param, self.min, self.max]
        else:
            return [self.code, chance, self.param, self.min, self.max]

class PropsTableMixin:
    def collect_props(self):
        props = []
        for entry in self.entries:
            entry_props = entry.get_all_props()
            props.append(entry_props)
        return props

    def mix_props(self):
        cols = []

        for type_ in self.entry_cls.prop_types.keys():
            cols += list(self.entry_cls.prop_cols_iter(type_))

        self.mix_cols(utils.flatten(cols))


class PropsRowMixin:
    @classmethod
    def get_prop_options(cls, type_):
        options = cls.prop_types[type_]
        return options["max_props"], options["temps"], options.get("first_prop_no", 1)

    @classmethod
    def prop_cols_iter(cls, type_):
        max_props, temps, first_prop_no = cls.get_prop_options(type_)

        for i in range(first_prop_no, max_props+first_prop_no):
            yield [temp.format(i) for temp in temps]

    def get_prop_amounts(self):
        return {type_: r.randint(1,options["max_props"]) for type_, options in self.prop_types.items()}

    def get_props(self, type_):
        props_for_type = []
        for prop_cols in self.prop_cols_iter(type_):
            values = self.get_multiple(prop_cols)
            if values[0] == "":
                continue
            props_for_type.append(Prop(*values, lvl=self.get_lvl()))
        return props_for_type

    def get_all_props(self):
        all_props = []
        for type_ in self.prop_types.keys():
            all_props.append(self.get_props(type_))
        return utils.flatten(all_props)

    def overwrite(self, type_, props):
        props = utils.assure_list(props)
        l = len(props)
        for i, prop_cols in enumerate(self.prop_cols_iter(type_)):
            if i >= l:
                values = [""] * len(prop_cols)
            else:
                values = props[i].as_list()
            self.set_multiple(prop_cols, values)

class RndPropsPool:
    def __init__(self, tables):
        self.tables = tables
        all_props = []
        for tbl in tables:
            all_props += tbl.collect_props()
        self.all_props = utils.flatten(all_props)
        # self.all_props = sorted(utils.flatten(all_props), key=lambda x: x.lvl)



    def redistribute(self):
        r.shuffle(self.all_props)
        prop_l = len(self.all_props)
        prop_idx_start = 0
        for tbl in self.tables:
            for e in tbl.entries:
                amounts = e.get_prop_amounts()
                for type_, options in e.prop_types.items():
                    amount = amounts[type_]
                    prop_idx_end = prop_idx_start + amount
                    if prop_idx_end > prop_l:
                        r.shuffle(self.all_props)
                        prop_idx_start = 0
                        prop_idx_end = amount
                    new_props = self.all_props[prop_idx_start:prop_idx_end]
                    e.overwrite(type_, new_props)
                    prop_idx_start = prop_idx_end

    def get_prop_groups(self):
        sorted_by_lvl = sorted(self.all_props, key=lambda x: x.lvl)
        prop_groups = utils.split_list(sorted_by_lvl, 3)
        return {group[-1].lvl: group for group in prop_groups}

    # def additional_props(self):
    #     props = []
    #     if options.ADD_OSKILL_CHANCE > 0:
    #         gen = PropGen("oskill")
    #         oskill_props = gen.gen_until_fail(options.ADD_OSKILL_CHANCE)
    #         for p in oskill_props:
    #             props.append(p)
    #     return props
        
    def redistribute_by_lvl(self):
        prop_groups = self.get_prop_groups()
        prop_groups_sets = {key: set(group) for key, group in prop_groups.items()}
        for tbl in self.tables:
            for e in tbl.entries:
                amounts = e.get_prop_amounts()
                lvl = e.get_lvl()
                for max_lvl in prop_groups.keys():
                    if lvl < max_lvl:
                        props = prop_groups_sets[max_lvl]
                        break
                for type_, options in e.prop_types.items():
                    amount = amounts[type_]
                    if amount > len(props):
                        props = prop_groups_sets[max_lvl] = set(prop_groups[max_lvl])
                    new_props = r.sample(props, amount)
                    props -= set(new_props)
                    e.overwrite(type_, new_props)

    def write(self):
        for tbl in self.tables:
            tbl.write()


class PropGen:
    CODES = utils.flatten([g["codes"] for g in proptypes.PROPERTY_GROUPS])
    def __init__(self, code=None, params=None):
        if code is None:
            code = r.choice(self.CODES)
        self.code = code
        for g in proptypes.PROPERTY_GROUPS:
            if code in g["codes"]:
                self.values = g["values"]
                break
        self.params = params

    def gen_prop(self, min=None, max=None, chance=None):
        min_ = min or self.values.get("min", "")
        if isinstance(min_, list):
            min_ = r.randint(*min_)

        max_ = max or self.values.get("max", "")
        if isinstance(max_, list):
            max_ = r.randint(*max_)
            if min_ and max_ < min_:
                max_ = min_

        if self.params:
            param = r.choice(self.params)
        else:
            param = self.values["param"]()


        # random lvl for now. Maybe based on prop values and type in the future
        lvl = r.randint(1,100)

        return Prop(code=self.code, param=param, min=min_, max=max_, lvl=lvl, chance=chance)

    def gen_until_fail(self, chance, max_=3):
        generated_props = []
        while len(generated_props) < max_:
            if randtools.chance(chance):
                generated_props.append(self.gen_prop())
            else:
                break
        return generated_props
