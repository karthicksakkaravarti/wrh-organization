#!/bin/bash
git clone https://github.com/we-race-here/wrh-organization.git /home/jenkins/wrh-organization
cd /home/jenkins/wrh-organization
git checkout karthick_master
mkdir -p media

sudo cp -rf ../nginx.conf  /etc/nginx/nginx.conf
sudo cp -rf ../default.conf  /etc/nginx/sites-available/default
pip install uwsgi
python manage.py collectstatic

# Restart nginx
sudo /etc/init.d/nginx start || sudo /etc/init.d/nginx start

# Running Celery
#celery -A wrh-organization worker -l info &
#celery -A wrh-organization beat &

# Running Server
uwsgi --socket mysite.sock --module wrh-organization.wsgi --buffer-size=100000 --chmod-socket=666 --master --processes 4 --threads 2