FROM debian:jessie
MAINTAINER ld86

RUN apt-get update; apt-get -y upgrade
RUN apt-get install -y python2.7 python-pip
RUN pip install Flask

ADD main.py /root/

CMD ["/usr/bin/python2.7", "/root/main.py"]
