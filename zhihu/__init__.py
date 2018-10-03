import os
import re
from pypinyin import lazy_pinyin

log = print


def ensure_path(p):
    d = os.path.dirname(p)
    if not os.path.exists(d):
        os.makedirs(d)


def str_filtered(s):
    r = re.sub('[\/:*?"<>|]', '-', s)
    return r


def sorted_pinyin(arr):
    return sorted(arr, key=lambda e: ''.join(lazy_pinyin(e)))
