#!/bin/sh
# Restore the production stack from a backup.
#
#   cd infra
#   sh backup/restore.sh backups/db/swafy-20261114-020000.dump
#
# Replaces the database with the dump, then copies the photos from
# BACKUP_DIR/photos back into MinIO. Stop the api and worker first:
#   docker compose -f docker-compose.prod.yml --env-file prod.env stop api worker
set -eu
# Stop Git Bash on Windows from rewriting /bin/sh into a Windows path.
export MSYS_NO_PATHCONV=1

DUMP="${1:?usage: sh backup/restore.sh <path to .dump file>}"
COMPOSE="docker compose -f docker-compose.prod.yml --env-file prod.env"

[ -f "$DUMP" ] || { echo "Not found: $DUMP"; exit 1; }

echo "Restoring database from $DUMP ..."
$COMPOSE exec -T db sh -c 'pg_restore --clean --if-exists --no-owner -U "$POSTGRES_USER" -d "$POSTGRES_DB"' < "$DUMP"

echo "Restoring photos ..."
$COMPOSE run --rm --no-deps --entrypoint /bin/sh photo-backup -c '
  mc alias set local http://minio:9000 "$MINIO_ROOT_USER" "$MINIO_ROOT_PASSWORD" >/dev/null &&
  mc mirror --overwrite /backups/photos/public local/public &&
  mc mirror --overwrite /backups/photos/quarantine local/quarantine'

echo "Done. Start the api and worker again:"
echo "  $COMPOSE up -d"
