#!/usr/bin/env python2
#-*- coding: utf-8 -*-
import requests
from lxml.builder import E
from lxml import etree
from flask import *

app = Flask(__name__)

def make_header(args=None):
    header = {'User-Agent': 'Kindle'}
    if args:
        for k, v in args.items():
            header[k] = v.encode('gbk')
    return header

def to_utf8_content(content):
    return content.decode('gbk').replace('gb2312', 'utf-8')

@app.route('/login/', methods=['POST'])
def login():
    user = request.form.get('username')
    passwd = request.form.get('password')
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {'loginmode': 'jjwxc', 'loginname': user, 'loginpass': passwd}
    r = requests.post('http://m.jjwxc.net/login/wapLogin', data=data,
                      headers=headers, allow_redirects=False)
    resp = redirect('/')
    for key, value in r.cookies.items():
        resp.set_cookie(key, value)
    return resp

@app.route('/')
def index():
    url = 'http://m.jjwxc.net/'
    r = requests.get(url, make_header(), cookies=session)
    body = etree.HTML(r.content.decode('gbk')).find('body')
    content = ''.join([etree.tostring(c) for c in body.getchildren()])
    return render_template('index.html', content=content)

@app.route('/<path:path>')
def origin(path):
    url = 'http://m.jjwxc.net/' + path
    r = requests.get(url, make_header(request.args.to_dict()), cookies=session)
    return to_utf8_content(r.content)

@app.route('/wap/<path:path>')
@app.route('/images/<path:path>')
@app.route('/favicon.ico')
def static_file(path=None):
    _ = path
    url = 'http://m.jjwxc.net/' + request.path
    return requests.get(url, make_header(), cookies=session).content

@app.route('/book2/<path:path>')
def book_page(path):
    url = 'http://m.jjwxc.net/book2/' + path
    if '/' not in path or path.split('/', 1)[1] is None:
        r = requests.get(url, make_header(), cookies=session)
        return to_utf8_content(r.content)

    r = requests.get(url, make_header(), cookies=session)
    book, chapter = path.split('/')[:2]
    dom = etree.HTML(r.content.decode('gbk'))
    content = etree.tostring(dom.xpath('.//div[@class="b module"]')[0])

    def make_menu(book, chapter):
        h2 = E.h2()
        if int(chapter) > 1:
            h2.append(E.a(u'上一章', href='/book2/%s/%d' % (book, chapter - 1),
                          style='float: left'))
        h2.append(E.a(u'返回书目', href='/book2/%s' % book,
                      style='position: absolute; left: 50%%'))
        h2.append(E.a(u'下一章', href='/book2/%s/%d' % (book, chapter + 1),
                      style='float: right'))
        h2.append(E.br())
        return etree.tostring(h2)
    menu = make_menu(book, int(chapter))
    content = render_template('base.html', body=menu + content + menu)
    return content

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='8080')
