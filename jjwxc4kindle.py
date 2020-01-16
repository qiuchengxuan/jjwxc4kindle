#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import logging
import signal
import sys
import threading

import requests
from flask import Flask, redirect, render_template, request
from gevent import monkey
from gevent.pywsgi import WSGIServer
from lxml import etree
from lxml.builder import E

app = Flask(__name__)
LOG = logging.getLogger(__name__)


def to_utf8_content(content):
    return content.decode('gbk').replace('gb2312', 'utf-8')


@app.route('/login/wapLogin', methods=['POST'])
def login():
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {'login_mode': 'jjwxc'}
    data.update(request.form)
    url = 'https://m.jjwxc.net/login/wapLogin'
    r = requests.post(url, data, headers=headers, allow_redirects=False)
    resp = redirect('/')
    for key, value in r.cookies.items():
        resp.set_cookie(key, value)
    return resp


@app.route('/buy/buy_vip', methods=['POST'])
def buy_vip():
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = dict(request.form)
    url = 'https://m.jjwxc.net/buy/buy_vip',
    r = requests.post(url, data, headers=headers, cookies=request.cookies, allow_redirects=False)
    if r.status_code == 302:
        url = r.headers['Location'].replace('https://m.jjwxc.net', '')
        return redirect(url)
    return to_utf8_content(r.content).replace('https://m.jjwxc.net', '')


@app.route('/rstatic/<path:path>')
def static_site(path):
    url = 'https://static.jjwxc.net/' + path
    r = requests.get(url, request.headers, cookies=request.cookies)
    return to_utf8_content(r.content)


@app.route('/')
def index_page():
    url = 'https://m.jjwxc.net/'
    r = requests.get(url, request.headers, cookies=request.cookies)
    body = etree.HTML(r.content.decode('gbk')).find('body')
    content = ''.join([etree.tostring(c, encoding=str) for c in body.getchildren()])
    content = content.replace('static.jjwxc.net', request.host + '/rstatic')
    return render_template('index.html', content=content)


@app.route('/<path:path>')
def origin(path):
    url = 'https://m.jjwxc.net/' + path
    r = requests.get(url, request.headers, cookies=request.cookies)
    return to_utf8_content(r.content)


@app.route('/wap/<path:path>')
@app.route('/images/<path:path>')
@app.route('/favicon.ico')
def static_file(path=None):
    _ = path
    url = 'https://m.jjwxc.net/' + request.path
    return requests.get(url, request.headers, cookies=request.cookies).content


@app.route('/vip/<int:book>/<int:chapter>')
@app.route('/book2/<int:book>')
@app.route('/book2/<int:book>/<int:chapter>')
def book_page(book, chapter=None):
    _ = (book, chapter)
    url = 'https://m.jjwxc.net/' + request.path
    if chapter is None:
        r = requests.get(url, request.headers, cookies=request.cookies)
        return to_utf8_content(r.content)

    r = requests.get(url, request.headers, cookies=request.cookies, allow_redirects=False)
    if r.status_code == 302:
        url = r.headers['Location'].replace('https://m.jjwxc.net/', '')
        return redirect(url)
    html = etree.HTML(r.content.decode('gbk'))
    content, navigation, _ = html.xpath('.//ul')

    def make_menu():
        h2 = E.h2()
        links = navigation.xpath('.//a')
        for link in links:
            if link.text == u'上一章':
                link.attrib['style'] = 'float: left'
                h2.append(link)
            elif link.text == u'下一章':
                link.attrib['style'] = 'float: right'
                h2.append(link)
            elif link.text == u'回目录':
                link.attrib['style'] = 'position: absolute; left: 50%'
                h2.append(link)
        h2.append(E.br())
        return etree.tostring(h2, encoding=str)

    content = etree.tostring(content.find('li', encoding=str))
    menu = make_menu()
    content = render_template('base.html', body=menu + content + menu)
    return content


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, handlers=[logging.StreamHandler(sys.stdout)])

    parser = argparse.ArgumentParser()
    parser.add_argument('-H', '--host', help='specify listen address', default='127.0.0.1')
    parser.add_argument('-p', '--port', type=int, help='specify listen port', default=8000)
    args = parser.parse_args()

    monkey.patch_socket()
    monkey.patch_thread()

    LOG.debug(app.url_map)
    app.url_map.strict_slashes = False
    stop_event = threading.Event()

    def signal_handler(sig, frame):
        _ = (sig, frame)
        stop_event.set()

    for sig in [signal.SIGINT, signal.SIGTERM]:
        signal.signal(sig, signal_handler)

    WSGIServer((args.host, args.port), app, log=LOG).start()
    stop_event.wait()
