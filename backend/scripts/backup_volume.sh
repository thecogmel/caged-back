#!/bin/bash
set -x

docker run --rm -v followme_postgres:/var/lib/postgresql/data/ alpine tar -czv --to-stdout -C /var/lib/postgresql/data/ . > backup_postgres_data.tgz
docker run --rm -v followme_data:/opt/data alpine tar -czv --to-stdout -C /opt/data . > backup_backend_data.tgz
