from functools import reduce

def flatten(list_of_lists):
    return reduce(lambda x,y: x+y , list_of_lists)

def n_sized_chunks(lst, n):
    """return max n-sized chunks from lst."""
    return [lst[i:i+n] for i in range(0, len(lst), n)]

def split_list(lst, parts_num):
    l = len(lst)
    part_l = l // parts_num
    parts = []
    for idx in range(0, l, part_l):
        parts.append(lst[idx:idx+part_l])
    if len(parts) > parts_num:
        parts[-2] += parts[-1]
        del parts[-1]
    return parts

def diff_col_names(col, diff=None):
    names = {
        "normal": "",
        "nightmare": "(N)",
        "hell": "(H)"
    }
    if diff:
        return col+names[diff]
    return [col+val for val in names.values()]

def assure_in_range(x, min_, max_):
    if min_ is not None and x < min_:
        return min_
    if max_ is not None and x > max_:
        return max_
    return x

def get_idx_interval(idx, start, end, divisor=2):
    radius = int(idx // divisor)
    min_idx = max(idx-radius, start)
    max_idx = min(idx+radius+1, end)

    return [min_idx, max_idx]

def assure_list(l):
    if isinstance(l, list):
        return l
    elif isinstance(l, tuple):
        return list(l)
    else:
        return [l]
