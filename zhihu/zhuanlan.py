import requests
import time
import os
import json
from pyquery import PyQuery as pq
from . import log, ensure_path, str_filtered, sorted_pinyin
import pdfkit


def url_initial(zhuanlan_name):
    n = zhuanlan_name
    r = 'https://www.zhihu.com/api/v4/columns/{}/articles?\
include=data%5B%2A%5D.admin_closed_comment%2Ccomment_count%2Csuggest_edit%2Cis_title_image_full_screen%2Ccan_comment%2Cupvoted_followees%2Ccan_open_tipjar%2Ccan_tip%2Cvoteup_count%2Cvoting%2Ctopics%2Creview_info%2Cauthor.is_following&limit=20&offset=0'.format(
        n)
    return r


def root(zhuanlan_name):
    name = zhuanlan_name
    return os.path.join('cache', 'zhuanlan', name)


def all_post(zhuanlan_name):
    url = url_initial(zhuanlan_name)
    headers = {
        'origin': 'https://zhuanlan.zhihu.com',
        'referer': 'https://zhuanlan.zhihu.com/{}'.format(zhuanlan_name),
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
    }
    d = {}
    while True:
        r = requests.get(url, headers=headers)
        j = r.json()
        data = j['data']
        for post in data:
            e_id = post['id']
            e_title = str_filtered(post['title'])
            keys = d.keys()
            if e_id not in keys:
                d[e_title] = e_id
        if j['paging']['is_end']:
            break
        url = j['paging']['next']
        time.sleep(2)
    return d


def all_post_path(zhuanlan_name):
    name = zhuanlan_name
    r = root(name)
    p = os.path.join(r, '{}.json'.format(name))
    return p


def all_post_cached(zhuanlan_name):
    name = zhuanlan_name
    p = all_post_path(name)
    ensure_path(p)
    if os.path.exists(p):
        with open(p, 'r') as f:
            r = json.loads(f.read())
            return r
    else:
        with open(p, 'w+') as f:
            r = all_post(name)
            s = json.dumps(r, ensure_ascii=False, indent=2)
            f.write(s)
        return r


def id_by_title(zhuanlan_name, post_title):
    d = all_post_cached(zhuanlan_name)
    r = d[post_title]
    return r


def post(zhuanlan_name, post_title):
    headers = {
        'origin': 'https://zhuanlan.zhihu.com',
        'referer': 'https://zhuanlan.zhihu.com/{}'.format(zhuanlan_name),
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
    }
    post_id = id_by_title(zhuanlan_name, post_title)
    url = 'https://zhuanlan.zhihu.com/p/{}'.format(post_id)
    html = requests.get(url, headers=headers).text
    return html


def post_cached(zhuanlan_name, post_title):
    name = zhuanlan_name
    p = os.path.join(root(name), 'raw', '{}.html'.format(post_title))
    ensure_path(p)
    if os.path.exists(p):
        with open(p, 'r') as f:
            r = f.read()
            return r
    else:
        with open(p, 'w+') as f:
            s = post(name, post_title)
            f.write(s)
            time.sleep(2)
            return s


def download_img(zhuanlan_name, src):
    name = zhuanlan_name
    t = str_filtered(src.split('/')[-1])
    p = os.path.join(root(name), 'prettified', 'img', t)
    ensure_path(p)
    if not os.path.exists(p):
        r = requests.get(src)
        with open(p, 'wb+') as f:
            f.write(r.content)


def post_prettified(zhuanlan_name, post_title):
    html = post_cached(zhuanlan_name, post_title)
    dom = pq(html)
    arr = [
        '.PostIndex-Contributes',
        'script',
        '#data',
        '.ColumnPageHeader-Wrapper',
        'meta[data-react-helmet="true"]',
        'link[rel="dns-prefetch"]',
        'link[rel="search"]',
        'meta[name="description"]',
        'noscript',
        '.FollowButton',
        '.Voters',
        '.Reward',
    ]
    for i in arr:
        dom.remove(i)
    for i in dom.find('img'):
        e = pq(i)
        src = e.attr('data-original') or e.attr('data-actualsrc') or e.attr('src')
        f = str_filtered(src.split('/')[-1])
        p = 'img/{}'.format(f)
        e.attr('src', p)
        download_img(zhuanlan_name, src)
    dom('link[rel="stylesheet"]').attr('href', 'css/post.css')
    return dom.outer_html()


def post_prettified_cached(zhuanlan_name, post_title):
    name = zhuanlan_name
    p = os.path.join(root(name), 'prettified', '{}.html'.format(post_title))
    ensure_path(p)
    if os.path.exists(p):
        with open(p, 'r') as f:
            s = f.read()
            return s
    else:
        with open(p, 'w+') as f:
            s = post_prettified(zhuanlan_name, post_title)
            f.write(s)
            return s


def generate_css(zhuanlan_name):
    name = zhuanlan_name
    p = os.path.dirname(__file__)
    f = os.path.join(p, 'template', 'post.css')
    p = os.path.join(root(name), 'prettified', 'css', 'post.css')
    ensure_path(p)
    with open(f, 'r') as f1:
        s = f1.read()
        with open(p, 'w+') as f2:
            f2.write(s)


def download_and_prettify(zhuanlan_name):
    d = all_post_cached(zhuanlan_name)
    for i in d.keys():
        u = 'https://zhuanlan.zhihu.com/p/{}'.format(d[i])
        log('download {}'.format(d[i]), i)
        post_prettified_cached(zhuanlan_name, i)
    generate_css(zhuanlan_name)


def generate_pdf(zhuanlan_name):
    name = zhuanlan_name
    download_and_prettify(zhuanlan_name)
    p = os.path.join(root(name), 'prettified')
    arr = filter(lambda e: e.endswith('.html'), os.listdir(p))
    arr = sorted_pinyin(list(arr))
    input = [os.path.join(p, i) for i in arr]
    f = os.path.join('out', 'zhuanlan-{}.pdf'.format(name))
    ensure_path(f)
    log('starting generate pdf............')
    pdfkit.from_file(input, f)
    log('generate pdf succeed')
