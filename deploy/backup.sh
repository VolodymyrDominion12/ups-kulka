#!/bin/sh
# Daily database dump and media archive into /backups (DATA_DIR/backups on the host).
# Copy that folder off the server too: a backup on the same disk does not survive the disk.
set -eu
KEEP_DAYS="${KEEP_DAYS:-14}"

while true; do
  stamp="$(date -u +%Y-%m-%dT%H%M)"
  if pg_dump --format=custom --file="/backups/db-$stamp.dump.part"; then
    mv "/backups/db-$stamp.dump.part" "/backups/db-$stamp.dump"
    echo "backup: db-$stamp.dump"
  else
    echo "backup: pg_dump failed" >&2
    rm -f "/backups/db-$stamp.dump.part"
  fi
  # Media files never change after upload, so one archive per week is enough.
  if [ "$(date -u +%u)" = "1" ] || ! ls /backups/media-*.tar.gz >/dev/null 2>&1; then
    tar -czf "/backups/media-$stamp.tar.gz.part" -C /data media \
      && mv "/backups/media-$stamp.tar.gz.part" "/backups/media-$stamp.tar.gz" \
      && echo "backup: media-$stamp.tar.gz"
  fi
  find /backups -name 'db-*.dump' -mtime "+$KEEP_DAYS" -delete
  find /backups -name 'media-*.tar.gz' -mtime "+$KEEP_DAYS" -delete
  sleep 86400
done
