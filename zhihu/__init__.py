import os
import re
from pypinyin import lazy_pinyin
import json

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


def cookie():
    p = os.path.dirname(__file__)
    n = os.path.join(p, 'config.json')
    with open(n, 'r') as f:
        s = f.read()
        r = json.loads(s)
        c = r['cookie']
        return c
