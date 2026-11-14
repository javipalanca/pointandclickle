#!/usr/bin/env bash
# Deploy the latest master on the production server.
#
#   ./update.sh
#
# 1. pulls master (fast-forward only),
# 2. tags the running Django image as :previous for a rollback,
# 3. builds the images while the site keeps running,
# 4. backs up the database and applies the migrations,
# 5. recreates only the containers whose image or configuration changed.
#
# When the Point and Click Museum shares this server, Traefik is also attached to its `edge`
# network (production.edge.yml); leaving that file out would take the museum offline.
#
# Rollback:
#   docker tag point_and_clickle_production_django:previous point_and_clickle_production_django
#   docker compose -f production.yml [-f production.edge.yml] up -d --no-deps django
#   (and, if the migrations must be undone, restore the backup this script made:
#    docker compose -f production.yml exec postgres restore <file>)

set -o errexit
set -o pipefail
set -o nounset

cd "$(dirname "$0")"

IMAGE=point_and_clickle_production_django
compose=(docker compose -f production.yml)
if [[ -f production.edge.yml ]] && docker network inspect edge >/dev/null 2>&1; then
    compose+=(-f production.edge.yml)
fi

step() { printf '\n\033[1m==> %s\033[0m\n' "$*"; }

step "Pulling master"
git pull --ff-only

step "Tagging the current image as ${IMAGE}:previous"
docker image inspect "${IMAGE}" >/dev/null 2>&1 && docker tag "${IMAGE}" "${IMAGE}:previous" || echo "no image yet"

step "Building images (the site keeps running)"
"${compose[@]}" build

step "Backing up the database"
"${compose[@]}" up -d postgres
"${compose[@]}" exec -T postgres backup

step "Applying migrations"
"${compose[@]}" run --rm django python manage.py migrate --noinput

step "Starting the new containers"
"${compose[@]}" up -d

step "Status"
"${compose[@]}" ps
