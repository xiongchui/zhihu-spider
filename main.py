from zhihu import zhuanlan, post
from multiprocessing import Pool

log = print


def txt():
    with open('list.txt', 'r') as f:
        return f.read()


def parsed_url(url):
    zhuanlan = 'https://zhuanlan.zhihu.com/'
    people = 'https://www.zhihu.com/people/'
    post = '/posts'
    if url.startswith(zhuanlan):
        name = url.split('/')[-1]
        return 'zhuanlan', name
    elif url.startswith(people) and url.endswith(post):
        name = url.split('/')[-2]
        return 'post', name


def generate_pdf(url):
    m, n = parsed_url(url)
    d = {
        'zhuanlan': zhuanlan.generate_pdf,
        'post': post.generate_pdf,
    }
    fn = d[m]
    fn(n)


if __name__ == '__main__':
    p = Pool()
    t = txt()
    arr = [i for i in t.split('\n') if i != '']
    log(arr)
    for i in arr:
        p.apply_async(generate_pdf, args=(i,))
    p.close()
    p.join()
    log('all process succeed')
