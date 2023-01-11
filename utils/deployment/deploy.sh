#!/bin/bash
git clone https://github.com/karthicksakkaravarti/wrh-organization.git /home/jenkins/wrh-organization
cd /home/jenkins/wrh-organization
git checkout dev2
mkdir -p media

sudo cp -rf ../nginx.conf  /etc/nginx/nginx.conf
sudo cp -rf ../default.conf  /etc/nginx/sites-available/default
cp ../.env /home/jenkins/wrh-organization/wrh_organization/wrh_organization/settings
cp ../local.py /home/jenkins/wrh-organization/wrh_organization/wrh_organization/settings
cp -rf ../dist /home/jenkins/wrh-organization/wrh_organization/FRONTEND/wrh_organization_ui

pip install uwsgi

#Running Build
#cd wrh_organization/FRONTEND/wrh_organization_ui
#yarn install
#yarn build

cd /home/jenkins/wrh-organization/wrh_organization

# Restart nginx
python manage.py collectstatic

sudo /etc/init.d/nginx start || sudo /etc/init.d/nginx start

# Running Server
uwsgi --socket mysite.sock --module wrh_organization.wsgi --buffer-size=100000 --chmod-socket=666 --master --processes 4 --threads 2