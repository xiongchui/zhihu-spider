import requests
import time
import os
import json
from pyquery import PyQuery as pq
from . import log, ensure_path, str_filtered, sorted_pinyin, cookie
import pdfkit


def url_offset(people_name, offset=0):
    n = people_name
    r = 'https://www.zhihu.com/api/v4/members/{}/articles?include=data%5B*%5D.comment_count%2Csuggest_edit%2Cis_normal%2Cthumbnail_extra_info%2Cthumbnail%2Ccan_comment%2Ccomment_permission%2Cadmin_closed_comment%2Ccontent%2Cvoteup_count%2Ccreated%2Cupdated%2Cupvoted_followees%2Cvoting%2Creview_info%3Bdata%5B*%5D.author.badge%5B%3F(type%3Dbest_answerer)%5D.topics&offset={}&limit=20&sort_by=created'.format(
        n, offset)
    return r


def root(people_name):
    name = people_name
    return os.path.join('cache', 'post', name)


def headers_posts_by_name(people_name):
    name = people_name
    headers = {
        'referer': 'https://www.zhihu.com/people/{}/posts'.format(name),
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
    }
    return headers


def header_post(people_name):
    name = people_name
    headers = {
        'origin': 'https://zhuanlan.zhihu.com',
        'referer': 'https://www.zhihu.com/people/{}/posts'.format(name),
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
        'Cookie': cookie()
    }
    return headers


def post_count(people_name):
    name = people_name
    headers = headers_posts_by_name(name)
    u = url_offset(name)
    r = requests.get(u, headers=headers)
    c = r.json()['paging']['totals']
    return c


def all_post(people_name):
    name = people_name
    headers = headers_posts_by_name(people_name)
    d = {}
    total = post_count(name)
    for i in range(0, total, 20):
        u = url_offset(name, i)
        r = requests.get(u, headers=headers)
        j = r.json()
        data = j['data']
        for post in data:
            e_id = post['id']
            e_title = str_filtered(post['title'])
            keys = d.keys()
            if e_id not in keys:
                d[e_title] = e_id
        time.sleep(2)
    return d


def all_post_path(people_name):
    name = people_name
    r = root(name)
    p = os.path.join(r, '{}.json'.format(name))
    return p


def all_post_cached(people_name):
    name = people_name
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


def id_by_title(people_name, post_title):
    d = all_post_cached(people_name)
    r = d[post_title]
    return r


def post(people_name, post_title):
    name = people_name
    headers = header_post(people_name)
    post_id = id_by_title(people_name, post_title)
    url = 'https://zhuanlan.zhihu.com/p/{}'.format(post_id)
    html = requests.get(url, headers=headers).text
    return html


def post_cached(people_name, post_title):
    name = people_name
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


def download_img(people_name, src):
    name = people_name
    t = str_filtered(src.split('/')[-1])
    p = os.path.join(root(name), 'prettified', 'img', t)
    ensure_path(p)
    if not os.path.exists(p):
        r = requests.get(src)
        with open(p, 'wb+') as f:
            f.write(r.content)


def post_prettified(people_name, post_title):
    html = post_cached(people_name, post_title)
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
        p = '../img/{}'.format(f)
        e.attr('src', p)
        download_img(people_name, src)
    dom('link[rel="stylesheet"]').attr('href', '../css/post.css')
    for i in dom.find('.UserLink-link'):
        e = pq(i)
        href = e.attr('href')
        if href.startswith('//'):
            e.attr('href', 'https:{}'.format(href))
    return dom.outer_html()


def post_prettified_cached(people_name, post_title):
    name = people_name
    p = os.path.join(root(name), 'prettified', 'html', '{}.html'.format(post_title))
    ensure_path(p)
    if os.path.exists(p):
        with open(p, 'r') as f:
            s = f.read()
            return s
    else:
        with open(p, 'w+') as f:
            s = post_prettified(people_name, post_title)
            f.write(s)
            return s


def generate_css(people_name):
    name = people_name
    p = os.path.dirname(__file__)
    f = os.path.join(p, 'template', 'post.css')
    p = os.path.join(root(name), 'prettified', 'css', 'post.css')
    ensure_path(p)
    with open(f, 'r') as f1:
        s = f1.read()
        with open(p, 'w+') as f2:
            f2.write(s)


def download_and_prettify(people_name):
    d = all_post_cached(people_name)
    for i in d.keys():
        u = 'https://zhuanlan.zhihu.com/p/{}'.format(d[i])
        log('download {}'.format(d[i]), i)
        post_prettified_cached(people_name, i)
    generate_css(people_name)


def generate_pdf(people_name):
    name = people_name
    download_and_prettify(people_name)
    p = os.path.join(root(name), 'prettified', 'html')
    arr = filter(lambda e: e.endswith('.html'), os.listdir(p))
    arr = sorted_pinyin(list(arr))
    input = [os.path.join(p, i) for i in arr]
    f = os.path.join('out', 'post-{}.pdf'.format(name))
    ensure_path(f)
    log('starting generate pdf............')
    pdfkit.from_file(input, f)
    log('generate pdf succeed')
