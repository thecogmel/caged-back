#!/bin/bash
set -x

PATH_BACKUP=$1

if [[ ! -e "$PATH_BACKUP/backup_postgres_data.tgz" ]]; then
  echo "Fail to restore backup, cannot find file $PATH_BACKUP/backup_postgres_data.tgz"
  exit 1
fi

if [[ ! -e "$PATH_BACKUP/backup_backend_data.tgz" ]]; then
  echo "Fail to restore backup, cannot find file $PATH_BACKUP/backup_backend_data.tgz"
  exit 1
fi

cat $PATH_BACKUP/backup_postgres_data.tgz | docker run --rm -i -v followme-admin_followme_postgres:/var/lib/postgresql/data/ alpine tar xzf - -C /var/lib/postgresql/data/
cat $PATH_BACKUP/backup_backend_data.tgz | docker run --rm -i -v followme-admin_followme_data:/opt/data alpine tar xzf - -C /opt/data

