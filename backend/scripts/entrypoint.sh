#!/bin/bash

create_superuser() {
  local cmd="from django.contrib.auth.models import User;               \
             User.objects.create_superuser('${BACKEND_ADMIN_USER}',    \
                                           '${BACKEND_ADMIN_EMAIL}',                          \
                                           '${BACKEND_ADMIN_PASSWORD}')"

  if [ -z ${BACKEND_ADMIN_USER+x} ]; then
    echo "[ERROR] Fail to create super user, the environment variable BACKEND_ADMIN_USER is not defined"
    exit 1
  fi

  if [ -z ${BACKEND_ADMIN_PASSWORD+x} ]; then
    echo "[ERROR] Fail to create super user, the environment variable BACKEND_ADMIN_PASSWORD is not defined"
    exit 1
  fi

  export DJANGO_SUPERUSER_PASSWORD=${BACKEND_ADMIN_PASSWORD}
  export DJANGO_SUPERUSER_USERNAME=${BACKEND_ADMIN_USER}
  export DJANGO_SUPERUSER_EMAIL=${BACKEND_ADMIN_EMAIL}

  python manage.py createsuperuser --noinput
}

setup_database() {
  python manage.py migrate
}

load_setup_data() {

  if [ -z ${BACKEND_DATA_SETUP+x} ]; then
    return 0
  fi

  if [ ! -d ${BACKEND_DATA_SETUP} ]; then
    return 0
  fi

  local files=$(find ${BACKEND_DATA_SETUP} -type f -name '*.json' | sort)

  for file in ${files}
  do
    echo "Loading: ${file}"
    if python manage.py loaddata ${file} 2>&1 | grep -q "IntegrityError"; then
      echo "Skip: ${file} (IntegrityError)"
    else
      echo "Loaded: ${file}"
    fi
  done
}

setup_history() {
  python manage.py populate_history --auto
}

main() {
  setup_database
  create_superuser
  load_setup_data
  setup_history
  python manage.py runserver 0.0.0.0:${BACKEND_API_PORT}
}

main "$@"
