#!/usr/bin/env python
#-*- coding: utf-8 -*-
import re
import urllib2

import web
import sae

urls = (
    '/', 'index',
    '/(?!book2)(.*)', 'origin',
    '/book2/(.*)', 'book'
)

def openurl(url, web):
    opener = urllib2.build_opener()
    opener.addheaders = [('User-Agent', web.ctx.env['HTTP_USER_AGENT'])]
    cookie = web.cookies().get('Cookie')
    if cookie != None:
        opener.addheaders.append(('Cookie', cookie))
    return opener.open(url)

class index:
    def GET(self):
        res = openurl('http://m.jjwxc.net/', web)
        content = reduce(lambda a, b: a + b, res.readlines())
        return str(render.empty('jjwxc4kindle')) + content.decode('gbk').encode('UTF-8').replace('gb2312', 'utf-8')

class origin:
    def GET(self, name):
        res = openurl('http://m.jjwxc.net/' + name, web)
        content = reduce(lambda a, b: a + b, res.readlines())
        return str(render.empty('jjwxc4kindle')) + content.decode('gbk').encode('UTF-8').replace('gb2312', 'utf-8')

class book:
    def GET(self, name):
        if '/' not in name or name.split('/', 1)[1] == None:
            res = openurl('http://m.jjwxc.net/book2/' + name, web)
            content = reduce(lambda a, b: a + b, res.readlines())
            return str(render.empty('jjwxc4kindle')) + content.decode('gbk').encode('UTF-8').replace('gb2312', 'utf-8')
        res = openurl('http://m.jjwxc.net/book2/' + name, web)
        book, chapter = name.split('/')[:2]
        while 'b module' not in res.readline():
            pass
        content = res.readline().decode('gbk')
        content = content[content.index('>') + 1 : content.rindex('<') - 1]
        def make_menu(book, chapter):
            s = '<h2>'
            if int(chapter) > 1:
                s += u'<a href="/book2/%s/%d" style="float: left">上一章</a>'%(book, int(chapter) - 1)
            s += u'<a href="/book2/%s" style="position: absolute; left: 50%%">返回书目</a>'%book
            s += u'<a href="/book2/%s/%d" style="float: right">下一章</a>'%(book, int(chapter) + 1)
            return s + '</h2>'
        content += make_menu(book, chapter)
        while 'line' not in dir() or '</div>' not in line:
            line = res.readline().decode('gbk')
            content += line
        content += make_menu(book, chapter)
        return str(render.base('jjwxc4kindle')) + content.encode('UTF-8')

web.config.debug = True

render = web.template.render('templates/')
app = web.application(urls, globals())

application = sae.create_wsgi_app(app.wsgifunc())
