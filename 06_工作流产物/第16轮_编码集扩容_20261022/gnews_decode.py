# -*- coding: utf-8 -*-
"""Google News RSS 链接解码：把 news.google.com/rss/articles/... 还原成出版商原文 URL。

原理：文章页里带 data-n-a-sg（签名）与 data-n-a-ts（时间戳），
带上这两项向 DotsSplashUi.batchexecute 发 garturlreq，返回真实链接。
"""
import re, json, sys, urllib.parse, urllib.request, urllib.error
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'
REQ = ['garturlreq', [['X', 'X', ['X', 'X'], None, None, 1, 1, 'US:en', None, 1, None, None, None, None, None, 0, 1],
                      'X', 'X', 1, [1, 1, 1], 1, 1, None, 0, 0, None, 0]]


def decode(gn_url, timeout=20):
    """返回出版商 URL；失败返回 ''。"""
    try:
        req = urllib.request.Request(gn_url, headers={'User-Agent': UA})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            html = r.read().decode('utf-8', 'ignore')
        sg = re.search(r'data-n-a-sg="([^"]+)"', html)
        ts = re.search(r'data-n-a-ts="([^"]+)"', html)
        if not (sg and ts):
            return ''
        aid = gn_url.split('/articles/')[1].split('?')[0]
        payload = json.dumps(['Fbv4je', json.dumps(REQ[:1] + [REQ[1], aid, int(ts.group(1)), sg.group(1)])])
        body = urllib.parse.urlencode({'f.req': json.dumps([[json.loads(payload)]])}).encode()
        r2 = urllib.request.Request('https://news.google.com/_/DotsSplashUi/data/batchexecute', data=body,
                                    headers={'User-Agent': UA,
                                             'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'})
        with urllib.request.urlopen(r2, timeout=timeout) as resp:
            txt = resp.read().decode('utf-8', 'ignore')
        m = re.search(r'https?://[^\\"\s]+', txt)
        return m.group(0) if m else ''
    except Exception:
        return ''


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    u = open(sys.argv[1], encoding='utf-8').read().strip() if len(sys.argv) > 1 else ''
    print(decode(u) or 'FAIL')
