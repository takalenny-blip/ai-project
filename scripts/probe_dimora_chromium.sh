#!/usr/bin/env bash
set -euo pipefail

# Small VAIO P + Chromium probe for the authenticated DiMORA page.
# It does not save cookies, credentials, or profile data to the repository.
URL="${1:?usage: $0 DIMORA_URL [OUTPUT_HTML]}"
OUT="${2:-dimora-page.html}"
CHROMIUM_BIN="${CHROMIUM_BIN:-chromium}"
PROFILE_DIR="${DIMORA_CHROMIUM_PROFILE:-$HOME/.config/chromium}"

if [[ ! -x "$(command -v "$CHROMIUM_BIN")" ]]; then
  echo "ERROR: Chromium not found: $CHROMIUM_BIN" >&2
  exit 2
fi

echo "Closing any running Chromium before using its profile may be required." >&2
"$CHROMIUM_BIN" \
  --headless=new \
  --disable-gpu \
  --dump-dom \
  --user-data-dir="$PROFILE_DIR" \
  "$URL" > "$OUT"

if grep -q "GL_FAVPGM_DATA" "$OUT"; then
  echo "OK: GL_FAVPGM_DATA found in $OUT"
  exit 0
fi

echo "NOT_FOUND: GL_FAVPGM_DATA was not present in $OUT" >&2
exit 3
