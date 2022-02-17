#!/bin/bash

BRANCH=master
if [ -n "$1" ]; then
    BRANCH=$1
fi

echo "+++ installing required libs ..."
sudo apt-get update
# sudo apt-get install postgresql postgresql-contrib postgresql-server-dev-all -y
sudo apt-get install nginx -y
sudo apt-get install python-dev -y
sudo apt-get install python3-dev -y
sudo apt-get install python3-pip -y
sudo apt-get install git -y
sudo apt-get install supervisor -y
sudo apt-get install libjpeg-dev zlib1g-dev -y
sudo apt-get install libffi-dev -y
sudo apt-get install libcairo2 -y
sudo apt-get install pango1.0-tests -y
sudo apt-get install redis-server -y
sudo ln -s /usr/bin/pip3 /usr/bin/pip
sudo pip install virtualenv

# setup project
NAME="wrh_organization"
GITURL=https://github.com/we-race-here/wrh-organization.git
ROOTDIR=/opt/webapps
PROJECTDIR=${ROOTDIR}/${NAME}
DJANGODIR=${PROJECTDIR}/${NAME}
ENVDIR=${PROJECTDIR}/env
DJANGO_SETTINGS_MODULE=wrh_organization.settings.main
USER=appuser                                      # the user to run as
GROUP=appuser                                     # the group to run as

echo "+++ creating project workspace in: $PROJECTDIR"
sudo mkdir -p ${ROOTDIR}
sudo chown ${USER}:${GROUP} ${ROOTDIR} -R
mkdir -p ${PROJECTDIR}
mkdir -p ${PROJECTDIR}/run
mkdir -p ${PROJECTDIR}/logs
mkdir -p ${PROJECTDIR}/etc
mkdir -p ${PROJECTDIR}/tmp

if [ -d "$DJANGODIR" ]; then
    cd ${DJANGODIR}
    git reset --hard HEAD
    git pull origin --recurse-submodules
    git checkout ${BRANCH}
    git pull
else
    git clone --recursive ${GITURL} -b ${BRANCH} ${DJANGODIR}
fi
cp ${DJANGODIR}/wrh_organization/wrh_organization/settings/external_config_sample.py ${PROJECTDIR}/etc/external_config.py

virtualenv -p python3 ${ENVDIR}
source ${ENVDIR}/bin/activate

sudo cp ${DJANGODIR}/utils/deploy.sh /usr/local/bin/"$NAME"_deploy
sudo chmod +x /usr/local/bin/"$NAME"_deploy
sudo cp ${DJANGODIR}/utils/backup.sh /usr/local/bin/"$NAME"_backup
sudo chmod +x /usr/local/bin/"$NAME"_backup
sudo cp ${DJANGODIR}/utils/supervisord.conf /etc/supervisor/conf.d/${NAME}.conf
sudo cp ${DJANGODIR}/utils/nginx.conf /etc/nginx/sites-available/${NAME}.conf
sudo ln -sf /etc/nginx/sites-available/${NAME}.conf /etc/nginx/sites-enabled/${NAME}.conf
cp ${DJANGODIR}/utils/daphne_start.sh ${ENVDIR}/bin/
chmod +x ${ENVDIR}/bin/daphne_start.sh

cd ${DJANGODIR}
pip install -r requirements.txt
pip install daphne
cd ${DJANGODIR}/wrh_organization
python manage.py migrate --settings=${DJANGO_SETTINGS_MODULE} --noinput
python manage.py collectstatic --settings=${DJANGO_SETTINGS_MODULE} --noinput
sudo service supervisor restart
sudo supervisorctl restart ${NAME}
sudo service nginx restart

echo
echo "Finished!"
