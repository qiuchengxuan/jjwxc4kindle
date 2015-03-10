#!/usr/bin/env python
#-*- coding: utf-8 -*-
import re
from urllib2 import urlopen

import web
import sae

urls = (
    '/', 'index',
    '/getcontent', 'getcontent'
)

class index:
    def GET(self):
        with open('static/index.html') as f:
            content = f.read()
        return str(render.base('Kindle看晋江')) + content

class getcontent:
    def GET(self):
        i = web.input(bookid=None, chapterid=None)
        if i.bookid is None or i.chapterid is None or \
           not i.bookid.isdigit() or not i.chapterid.isdigit():
             return "invalid bookid or chapterid"

        res = urlopen('http://wap.jjwxc.net/book2/%s/%s'%\
                      (i.bookid, i.chapterid))
        while 'b module' not in res.readline():
            pass
        content = res.readline().decode('gbk')
        content = content[content.index('>')+1 : content.rindex('<')-1]
        if int(i.chapterid) > 1:
            content = u'<a href="/getcontent?bookid=%s&chapterid=%d" \
                      style="float:left">上一章</a>'%\
                      (i.bookid, int(i.chapterid)-1) + content
        content += u'<a href="/getcontent?bookid=%s&chapterid=%d" \
                   style="float:right">下一章</a>'%\
                   (i.bookid, int(i.chapterid)+1)
        content = '<h2>' + content + '</h2>'
        while 'line' not in dir() or '</div>' not in line:
            line = res.readline().decode('gbk')
            content += line
        content += '<h2>'
        if int(i.chapterid) > 1:
            content += u'<a href="/getcontent?bookid=%s&chapterid=%d" \
                       style="float:left">上一章</a>'%\
                       (i.bookid, int(i.chapterid)-1)
        content += u'<a href="/getcontent?bookid=%s&chapterid=%d" \
                   style="float:right">下一章</a>'%\
                   (i.bookid, int(i.chapterid)+1)
        content += '</h2>'
        return str(render.base('Kindle看晋江')) + content.encode('UTF-8')

web.config.debug = True

render = web.template.render('templates/')
app = web.application(urls, globals())

application = sae.create_wsgi_app(app.wsgifunc())
