import os
import csv
from shutil import copytree
from collections import defaultdict

from . import APP_ROOT
from . import utils
from . import headers
from .options import options
from . import randtools

r = randtools.r

TXT_DIR = os.path.join(APP_ROOT, "files/in/txt/")
DATA_DIR = os.path.join(APP_ROOT, "files/out/data/")
EXCEL_DIR = os.path.join(DATA_DIR, "global/excel")

def copy_data_dir(d2path):
    if options.DEBUG.enabled:
        print("DEBUG")
        return
    copytree(DATA_DIR, os.path.join(d2path, "data"), dirs_exist_ok=True)



class Row:
    FILE_NAME = None

    def __init__(self, idx, row, header):
        self.row = row
        self.idx = idx
        self.header = header
        self.name = row[0]

    def get_lvl(self):
        return 1

    def get_multiple(self, keys):
        vals = []
        for key in keys:
            vals.append(self.get(key))
        return vals

    def set_multiple(self, keys, vals):
        for key, val in zip(keys, vals):
            self.set(key, val)

    def get(self, key):
        idx = self.header[key]
        v = self.row[idx]
        try:
            v = int(v)
        except:
            pass
        return v

    def set(self, key, val):
        idx = self.header[key]
        try:
            val = round(val)
        except:
            pass
        self.row[idx] = str(val)

    def mul(self, cols, m):
        self.calc(cols, lambda x: x*m)

    def div(self, cols, m):
        self.calc(cols, lambda x: x/m)

    def calc(self, cols, fn):
        cols = utils.assure_list(cols)
        for col in cols:
            val = self.get(col)
            new_val = fn(val)
            new_val = round(new_val)
            self.set(col, new_val)


class Table:
    EXCLUDE = []
    FILE_NAME = None

    entry_cls = Row

    def __init__(self, file_name=None):
        if file_name is not None:
            self.FILE_NAME = file_name
        self.prepare()
        self.make_entries()

    def excluded(self, row):
        name = row[0]
        for entry in self.EXCLUDE:
            if callable(entry) and entry(row):
                return True
            elif isinstance(entry, dict):
                for key, val in entry.items():
                    idx = self.header_map[key]
                    if not isinstance(val, list):
                        val = [val]
                    if row[idx] in val:
                        return True
            elif entry == name or name == "":
                return True


    def prepare(self):
        path = os.path.join(TXT_DIR, "{}.txt".format(self.FILE_NAME))
        with open(path, "r", newline='', encoding="cp1252") as f:
            tsv_reader = csv.reader(f, delimiter='\t')
            self.header = next(tsv_reader)
            self.header_map = {name: idx for idx, name in enumerate(self.header)}
            rows = []
            for row in tsv_reader:
                rows.append(row)
            self.rows = rows
            self.row_len = len(row)

    def append_entry(self):
        row = [""] * self.row_len
        row[-1] = 0
        self.rows.append(row)
        entry = self.entry_cls(self.entry_idx, row, self.header_map)
        self.entries.append(entry)
        self.entry_idx += 1
        return entry


    def make_entries(self):
        entries = []
        entry_map = {}
        row_id_col = getattr(self, "ROW_ID", None) or self.header[0] 
        for idx, row in enumerate(self.rows):
            if self.excluded(row):
                continue
            entry = self.entry_cls(idx, row, self.header_map)
            entries.append(entry)
            entry_map[entry.get(row_id_col)] = entry
        self.entries = entries
        self.entry_map = entry_map
        self.entry_idx = idx+1

    def update_rows(self):
        for entry in self.entries:
            self.rows[entry.idx] = entry.get_row()

    def write(self):
        if options.DEBUG.enabled:
            print("DEBUG")
            return
        path = os.path.join(EXCEL_DIR, "{}.txt".format(self.FILE_NAME))
        with open(path, "w", encoding="cp1252") as f:
            tsv_writer = csv.writer(f, delimiter="\t")
            tsv_writer.writerow(self.header)
            tsv_writer.writerows(self.rows)

    def switch_cols(self, col_names, a, b):
        v_b, v_a = self.get_cols_values(col_names, [a,b])
        cols_maps = self.get_cols_maps(col_names, [v_a, v_b])
        self.apply_cols(cols_maps, [a, b])

    def mix_cols(self, col_names, entries=None):
        entries = entries or self.entries
        cols_values = self.get_cols_values(col_names, entries)
        r.shuffle(cols_values)
        cols_maps = self.get_cols_maps(col_names, cols_values)
        self.apply_cols(cols_maps, entries)

    def get_cols_values(self, col_names, entries=None):
        col_names = utils.assure_list(col_names)
        cols_values = []
        entries = entries or self.entries
        for entry in entries:
            cols_values.append([entry.get(col) for col in col_names])
        return cols_values

    def get_cols_maps(self, col_names, cols_values):
        return [{col_names[i]: val for i, val in enumerate(values)} for values in cols_values]

    def apply_cols(self, cols_maps, entries=None):
        entries = entries or self.entries
        for entry, cols_map in zip(entries, cols_maps):
            for col, val in cols_map.items():
                entry.set(col, val)

    def multiply_col(self, cols, m, min_=None, max_=None, entries=None):
        entries = entries or self.entries
        def mul(x):
            new_x = x*m
            new_x = utils.assure_in_range(new_x, min_, max_)
            return new_x
        self.manip_col(cols, mul, entries)

    def divide_col(self, cols, d, min_=None, max_=None, entries=None):
        entries = entries or self.entries

        def div(x):
            new_x = x // d
            new_x = utils.assure_in_range(new_x, min_, max_)
            return new_x
        self.manip_col(cols, div, entries)

    def add_col(self, cols, d, min_=None, max_=None, entries=None):
        entries = entries or self.entries

        def add(x):
            new_x = x + d
            new_x = utils.assure_in_range(new_x, min_, max_)
            return new_x
        self.manip_col(cols, add, entries)


    def manip_col(self, cols, fn, entries=None):
        cols = utils.assure_list(cols)
        entries = entries or self.entries

        for e in entries:
            for col in cols:
                val = e.get(col)
                try:
                    val = fn(val)
                except:
                    pass
                else:
                    e.set(col, val)

    def set_col(self, cols, vals, entries=None):
        cols = utils.assure_list(cols)
        vals = utils.assure_list(vals)
        assert len(cols) == len(vals)
        entries = entries or self.entries
        for e in entries:
            for col, val in zip(cols, vals):
                e.set(col, val)



    def sort_by_col(self, col):
        return sorted(self.entries, key=lambda x: x.get(col))

    # TODO: rename this
    def group_by_col(self, col, num, num_is_group_len=True):
        # if num_is_group_len all groups will have num elements (the last gets the rest).
        # Otherwise there will be num groups with the same number of elements (the last may have one more)
        entries = self.sort_by_col(col, is_int)
        if num_is_group_len:
            return utils.n_sized_chunks(entries, num)
        else:
            return utils.split_list(entries, num)



# class Tables(dict):
#     def __missing__(self, key):
#         t = Table(key)
#         self[key] = t
#         return t
# tables = Tables()

# print(tables["MagicPrefix"].header)
# breakpoint()


