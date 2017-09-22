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

@app.route('/login/wapLogin', methods=['POST'])
def login():
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {'loginmode': 'jjwxc'}
    data.update(request.form)
    r = requests.post('http://m.jjwxc.net/login/wapLogin', data,
                      headers=headers, allow_redirects=False)
    resp = redirect('/')
    for key, value in r.cookies.items():
        resp.set_cookie(key, value)
    return resp

@app.route('/buy/buy_vip', methods=['POST'])
def buy_vip():
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = dict(request.form)
    r = requests.post('http://m.jjwxc.net/buy/buy_vip', data,
                      headers=headers, cookies=request.cookies,
                      allow_redirects=False)
    if r.status_code == 302:
        url = r.headers['Location'].replace('http://m.jjwxc.net', '')
        return redirect(url)
    return to_utf8_content(r.content).replace('http://m.jjwxc.net', '')

@app.route('/static/<path:path>')
def static_site(path):
    url = 'http://static.jjwxc.net/' + path
    r = requests.get(url, make_header(request.args.to_dict()),
                     cookies=request.cookies)
    return to_utf8_content(r.content)

@app.route('/')
def index_page():
    url = 'http://m.jjwxc.net/'
    r = requests.get(url, make_header(request.args.to_dict()),
                     cookies=request.cookies)
    body = etree.HTML(r.content.decode('gbk')).find('body')
    content = ''.join([etree.tostring(c) for c in body.getchildren()])
    content.replace('static.jjwxc.net', 'static/')
    return render_template('index.html', content=content)

@app.route('/<path:path>')
def origin(path):
    url = 'http://m.jjwxc.net/' + path
    r = requests.get(url, make_header(request.args.to_dict()),
                     cookies=request.cookies)
    return to_utf8_content(r.content)

@app.route('/wap/<path:path>')
@app.route('/images/<path:path>')
@app.route('/favicon.ico')
def static_file(path=None):
    _ = path
    url = 'http://m.jjwxc.net/' + request.path
    return requests.get(url, make_header(request.args.to_dict()),
                        cookies=request.cookies).content

@app.route('/vip/<int:book>/<int:chapter>')
@app.route('/book2/<int:book>')
@app.route('/book2/<int:book>/<int:chapter>')
def book_page(book, chapter=None):
    _ = (book, chapter)
    url = 'http://m.jjwxc.net/' + request.path
    if chapter is None:
        r = requests.get(url, make_header(request.args.to_dict()),
                         cookies=request.cookies)
        return to_utf8_content(r.content)

    r = requests.get(url, make_header(request.args.to_dict()),
                     cookies=request.cookies, allow_redirects=False)
    if r.status_code == 302:
        url = r.headers['Location'].replace('http://m.jjwxc.net/', '')
        return redirect(url)
    dom = etree.HTML(r.content.decode('gbk'))
    div = dom.xpath('.//div[@class="b module"]')[0]

    def make_menu():
        h2 = E.h2()
        links = div.xpath('.//a')[:3]
        next_chapter = prev_chapter = index = None
        if links[0].text == u'下一章':
            if links[1].text == u'上一章':
                next_chapter, prev_chapter, index = links
            else:
                next_chapter, index, _ = links
        else:
            prev_chapter, index, _ = links
        if prev_chapter is not None:
            prev_chapter.attrib['style'] = 'float: left'
            h2.append(prev_chapter)
        index.attrib['style'] = 'position: absolute; left: 50%'
        h2.append(index)
        if next_chapter is not None:
            next_chapter.attrib['style'] = 'float: right'
            h2.append(next_chapter)
        h2.append(E.br())
        return etree.tostring(h2)
    content = etree.tostring(div)
    menu = make_menu()
    content = render_template('base.html', body=menu + content + menu)
    return content

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='8080')
