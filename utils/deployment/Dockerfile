
FROM python:3.8

RUN apt-get update && apt-get install vim sudo -y

RUN curl -sL https://deb.nodesource.com/setup_10.x | sudo -E bash -

RUN apt-get update && apt-get install build-essential -y

RUN apt-get update && apt-get install libldap2-dev -y

RUN apt-get update && apt-get install libsasl2-dev -y

RUN apt-get update && apt-get install python3-dev -y

RUN apt-get update && apt-get install tox -y

RUN apt-get update && apt-get install lcov -y

RUN apt-get update && apt-get install valgrind -y

RUN apt-get install nodejs nginx -y

RUN useradd -ms /bin/bash jenkins ; usermod -aG sudo jenkins

RUN echo "jenkins ALL=NOPASSWD: ALL" >> /etc/sudoers

RUN ln -fs /usr/share/zoneinfo/Asia/Kolkata /etc/localtime

#Port forwarding
EXPOSE 8001

USER jenkins

#Copying deploy script to the container
COPY ./requirement.txt /home/jenkins/

COPY .git-credentials /root/

COPY .git-credentials /home/jenkins/

COPY nginx.conf /home/jenkins/

COPY default.conf /home/jenkins/

WORKDIR /home/jenkins/

USER root

RUN pip install -r requirement.txt

RUN pip install uwsgi

RUN apt-get install cron -y

RUN git config --global credential.helper store

COPY --chown=jenkins:jenkins deploy.sh /home/jenkins/

ENTRYPOINT ["/bin/sh","/home/jenkins/deploy.sh"]