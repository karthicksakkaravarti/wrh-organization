#!/bin/bash

NAME="wrh_organization"                                  # Name of the application
ROOTDIR=/opt/webapps
PROJECTDIR=${ROOTDIR}/${NAME}
DJANGODIR=${PROJECTDIR}/${NAME}
ENVDIR=${PROJECTDIR}/env
SOCKFILE=${PROJECTDIR}/run/${NAME}.sock
DJANGO_SETTINGS_MODULE=wrh_organization.settings.main             # which settings file should Django use
DJANGO_ASGI_MODULE=wrh_organization.asgi                     # WSGI module name

echo "Starting ${NAME} as `whoami`"

# Activate the virtual environment
source ${ENVDIR}/bin/activate
export DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE}
export PYTHONPATH=${DJANGODIR}/wrh_organization:${PYTHONPATH}

# Create the run directory if it doesn't exist
RUNDIR=$(dirname ${SOCKFILE})
test -d ${RUNDIR} || mkdir -p ${RUNDIR}

# Start your Django Unicorn
# Programs meant to be run under supervisor should not daemonize themselves (do not use --daemon)
exec ${ENVDIR}/bin/daphne ${DJANGO_ASGI_MODULE}:application \
  --proxy-headers \
  -u ${SOCKFILE} \
  --access-log=${PROJECTDIR}/logs/daphne.log
