#!/usr/bin/env python2
#-*- coding: utf-8 -*-
import requests
from lxml.builder import E
from lxml import etree
from flask import Flask, request, render_template

app = Flask(__name__)

def make_header():
    header = {'User-Agent': 'Kindle'}
    return header

def to_utf8_content(content):
    return content.decode('gbk').replace('gb2312', 'utf-8')

@app.route('/my/<path:path>')
@app.route('/')
def index(path=None):
    _ = path
    url = 'http://m.jjwxc.net/' + request.path
    r = requests.get(url, make_header())
    return to_utf8_content(r.content)

@app.route('/wap/<path:path>')
@app.route('/images/<path:path>')
@app.route('/favicon.ico')
def raw(path=None):
    _ = path
    url = 'http://m.jjwxc.net/' + request.path
    return requests.get(url, make_header()).content

@app.route('/book2/<path:path>')
def book_page(path):
    if '/' not in path or path.split('/', 1)[1] is None:
        r = requests.get('http://m.jjwxc.net/book2/' + path, make_header())
        return to_utf8_content(r.content)

    r = requests.get('http://m.jjwxc.net/book2/' + path, make_header())
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
    content = render_template('base.html') + menu + content + menu
    return content

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='8080')
