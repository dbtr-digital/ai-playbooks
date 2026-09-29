#!/usr/bin/env python3
"""Sucht interne Namen in allen versionierten Dateien.

Die Musterliste ist NICHT Teil dieses Repos (sie enthält genau das, was nicht
öffentlich werden soll). Quelle, in dieser Reihenfolge:
  1. Umgebungsvariable INTERNAL_NAMES (ein Muster je Zeile; in GitHub als Secret)
  2. Datei aus AI_PLAYBOOKS_NAMES
  3. lokale, nicht versionierte Git-Einstellung:  git config ai-playbooks.namen <pfad>

Muster sind Python-Regex, Groß-/Kleinschreibung egal. Zeilen mit # sind Kommentare.
Die Ausgabe nennt nur Datei und Zeile, NIE den Treffer oder das Muster, weil
CI-Logs öffentlicher Repos öffentlich sind.

Exit: 0 sauber · 1 Treffer · 2 keine Musterliste gefunden
"""
import os, re, subprocess, sys, pathlib

root = pathlib.Path(__file__).resolve().parent.parent
src = os.environ.get("INTERNAL_NAMES")
if not src:
    cand = os.environ.get("AI_PLAYBOOKS_NAMES")
    if not cand:
        r = subprocess.run(["git", "config", "--get", "ai-playbooks.namen"], cwd=root,
                           capture_output=True, text=True)
        cand = r.stdout.strip()
    if cand:
        p = pathlib.Path(cand).expanduser()
        if not p.is_absolute():
            p = (root / p).resolve()
        if p.is_file():
            src = p.read_text(encoding="utf-8")
if not src:
    print("namen-check: KEINE Musterliste gefunden, nichts geprüft (exit 2)")
    sys.exit(2)

pats = []
for line in src.splitlines():
    line = line.strip()
    if line and not line.startswith("#"):
        pats.append(re.compile(line, re.I))

# Bewusst ausgenommen: Lizenz- und Urheberdateien. Dort steht der Rechteinhaber
# absichtlich mit Namen (Namensnennung nach CC BY 4.0 bzw. MIT).
ALLOWED_FILES = {"LICENSE", "LICENSE-CODE", "NOTICE"}

files = subprocess.run(["git", "ls-files", "-z"], cwd=root, capture_output=True, check=True).stdout.decode().split("\0")
hits = 0
for f in filter(None, files):
    if f in ALLOWED_FILES:
        continue
    try:
        text = (root / f).read_text(encoding="utf-8")
    except (UnicodeDecodeError, FileNotFoundError):
        continue
    for n, line in enumerate(text.splitlines(), 1):
        if any(p.search(line) for p in pats):
            print(f"TREFFER {f}:{n}")
            hits += 1

print(f"namen-check: {len(pats)} Muster, {hits} Treffer")
sys.exit(1 if hits else 0)
