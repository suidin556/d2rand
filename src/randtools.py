import random
import time
from .options import options
from . import utils


r = random.Random()

def chance(p):
    return True if r.random() < p/100 else False

def coin():
    return chance(50)

def rnd_sign():
    return 1 if coin() else -1


class BoundCurve:
    def __init__(self, lower, upper, exp=2, round=True):
        self.lower = lower
        self.upper = upper
        self.exp = exp
        self.round = round

    def get(self, amount=1):
        if amount == 1:
            return self.calc()
        results = []
        for _ in range(amount):
            results.append(self.calc())
        return results

    def calc(self):
        diff = self.upper - self.lower
        diff_half = diff / 2
        mid = upper - diff_half
        rnd_float = r.random()
        dist = (rnd_float ** self.exp) * diff_half
        sign = rnd_sign()
        # print(diff, mid, rnd_float, dist)
        result = mid + (sign*dist)
        if self.round:
            return round(result)
        else:
            return result


def mix_and_draw(boxes):
    # box_sizes = box_sizes or utils.flatten([[len(item) for item in box] for box in boxes])
    props = sorted(utils.flatten(utils.flatten(boxes)), key=lambda x: x.lvl)
    # r.shuffle(items)
    # r.shuffle(box_sizes)

    # idx = 0
    # l = len(items)
    # print("prop pool items: {}".format(l))
    while True:
        item = yield
        item_lvl = item.lvl
        # if idx % 500 == 0:
        #     print("prop pool idx: {}".format(idx))
        # if idx >= l:
        #     print("exhausted prop pool; reshuffling...")
        #     r.shuffle(items)
        #     idx = 0
        # yield items[idx]
        # idx += 1

    # for item in items:
    #     yield item


