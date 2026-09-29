#!/usr/bin/env bash
# Prüfung vor dem Veröffentlichen: Secret-Scan (gitleaks) + interne Namen.
#   bash scripts/pruefen.sh                 # prüfen
#   bash scripts/pruefen.sh --install-hook  # als pre-push-Hook in dieses Klon einhängen
# Exit ungleich 0 = nicht pushen.
set -u
DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/.." && pwd)"
cd "$DIR" || exit 2

if [ "${1:-}" = "--install-hook" ]; then
  printf '#!/usr/bin/env bash\nexec bash "%s/scripts/pruefen.sh"\n' "$DIR" > .git/hooks/pre-push
  chmod +x .git/hooks/pre-push
  echo "pre-push-Hook eingerichtet: jeder git push prüft vorher."
  exit 0
fi

rc=0
if command -v gitleaks >/dev/null 2>&1; then
  gitleaks git --no-banner --redact . || rc=1
else
  echo "FEHLT: gitleaks nicht installiert (macOS: brew install gitleaks) — Secret-Scan NICHT gelaufen"
  rc=2
fi

python3 scripts/namen-check.py
nc=$?
[ $nc -ne 0 ] && rc=$nc

[ $rc -eq 0 ] && echo "OK: nichts gefunden, Push freigegeben." || echo "STOPP: Befund oder unvollständige Prüfung (exit $rc)."
exit $rc
