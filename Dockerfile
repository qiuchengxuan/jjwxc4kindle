FROM python:2.7.13
MAINTAINER qiuchengxuan
ADD . /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 8080
CMD python /app/jjwxc4kindle.py