FROM alpine:3.7
MAINTAINER qiuchengxuan@gmail.com
ADD . /app
WORKDIR /app
RUN sed -i 's#http://dl-cdn.alpinelinux.org/#https://mirrors.tuna.tsinghua.edu.cn/#g' /etc/apk/repositories
RUN apk add --update python3 py3-flask py3-lxml py3-requests py3-gevent
EXPOSE 8000
CMD python3 /app/jjwxc4kindle.py -H 0.0.0.0
