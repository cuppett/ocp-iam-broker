#!/usr/bin/env sh
set -eu

envsubst '${OCP_BROKER_LOC}' < /etc/nginx/nginx.conf.TEMPLATE > /etc/nginx/nginx.conf

exec "$@"