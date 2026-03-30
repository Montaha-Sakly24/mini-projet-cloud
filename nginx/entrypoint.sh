#!/bin/sh
set -eu

CERT_DIR="/etc/nginx/certs"
CERT_KEY="$CERT_DIR/server.key"
CERT_CRT="$CERT_DIR/server.crt"

mkdir -p "$CERT_DIR"

if [ ! -f "$CERT_KEY" ] || [ ! -f "$CERT_CRT" ]; then
  # Self-signed cert for local/dev/CI usage.
  # Browsers/clients will require "insecure"/trusted cert import.
  openssl req -x509 -nodes -newkey rsa:2048 \
    -keyout "$CERT_KEY" \
    -out "$CERT_CRT" \
    -days 365 \
    -subj "/CN=localhost" >/dev/null 2>&1
fi

exec nginx -g "daemon off;"
