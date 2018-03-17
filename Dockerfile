FROM debian:stretch
MAINTAINER qiuchengxuan
ADD . /app
WORKDIR /app
RUN apt-get update
RUN apt-get -y --no-install-recommends install python python-flask python-lxml python-requests
EXPOSE 8000
CMD python /app/jjwxc4kindle.py -H 0.0.0.0
