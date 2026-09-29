# ai-playbooks

Regeldatei dieses Repos, **für jedes Werkzeug** (Claude Code, Codex, …). Kurz, weil das
Repo öffentlich ist: Hier steht nur, wer veröffentlicht und was vor jedem Push gilt.

## Was das ist

Eine öffentliche Sammlung von Anleitungen, die man einer KI gibt, damit sie mit einem
Menschen etwas aufbaut. Jedes Kapitel ist ein Ordner mit einer `README.md` und muss
**für sich allein** funktionieren. Übersicht und gemeinsame Grundsätze: [`README.md`](README.md).

## Wer hier veröffentlicht: geteilte Zuständigkeit

Das Repo gehört keinem einzelnen Arbeitsbereich. **Drei Stellen dürfen hier
gleichberechtigt Kapitel anlegen, ändern und pushen:**

| Wer | Typischer Beitrag |
|---|---|
| der Owner (Mensch) | Entscheidungen, Freigaben, eigene Kapitel |
| Sitzungen im Arbeitsbereich **Projekte** (projektübergreifende Verwaltung) | Kapitel zu projektübergreifender Arbeit: Doku-Struktur, Feedback-Kanal, Deploy-Verfahren, Agenten-Regeln, Prompts |
| Sitzungen im Arbeitsbereich **Server** (Serverbetrieb) | Kapitel zu Server-Sicherheit und -Betrieb |

- **Aus welchem Arbeitsbereich ein Kapitel stammt, steht nicht im Kapitel**, sondern im
  privaten Feedback-Kanal. Kapitel bleiben so von der eigenen Umgebung entkoppelt. Wer ein
  fremdes Kapitel inhaltlich ändert, meldet das dem Herkunftsbereich über diesen Kanal,
  statt es still umzuschreiben.
- **Keine Erfahrungswerte aus der eigenen Umgebung** in Kapiteln (Anzahl Server,
  gemessene Angriffszahlen, gewählte Sperrdauern als „unsere“). Wo eine Zahl nicht für
  die Anleitung nötig ist, fehlt sie.
- Rückmeldungen, Fragen und Vorschläge zwischen den Beteiligten laufen **nicht hier**,
  sondern im **privaten Feedback-Kanal** des Arbeitsbereichs Projekte. Wo er liegt, wissen
  die Beteiligten; er wird hier bewusst nicht genannt.
  Das Repo ist öffentlich; interne Abstimmung gehört nicht in seine Historie.

## Vor jedem Push: nichts Internes veröffentlichen

Das Repo ist **öffentlich**. Kapitel entstehen aus privaten Repos und müssen vorher
anonymisiert sein.

1. **Keine Geheimnisse:** keine Passwörter, Tokens, Schlüssel, geheimen URLs,
   Topic-Namen, Knock-Geheimnisse.
2. **Keine Infrastruktur:** keine IP-Adressen, Hostnamen, Domains, Servernamen,
   Hoster-Kundennummern, Pfade aus dem eigenen Home.
3. **Keine Personen und Projekte:** keine Namen, E-Mail-Adressen, internen
   Projekt- oder Repo-Namen (Ausnahme: diese Regeldatei).
4. **Muster statt Werte:** Platzhalter in `<spitzen Klammern>`. Gemessene Zahlen nur
   als Größenordnung ohne Bezug auf einen bestimmten Host.
5. **Prüfen, nicht hoffen:** vor jedem Push `bash scripts/pruefen.sh`. Das läuft
   `gitleaks` über die ganze Historie und sucht die privaten Namensmuster.
   Einmal je Klon `bash scripts/pruefen.sh --install-hook`, dann prüft jeder
   `git push` automatisch. Ein Treffer blockiert den Push.
   - Die Musterliste liegt **nicht hier**, sondern privat im Arbeitsbereich Projekte und
     als GitHub-Secret `INTERNAL_NAMES`. Lokal findet das Skript sie über die
     Umgebungsvariable `AI_PLAYBOOKS_NAMES` oder über die **nicht versionierte**
     Git-Einstellung dieses Klons:
     `git config ai-playbooks.namen <pfad-zur-liste>`. Wer ein neues internes Wort kennt (Projekt, Server, Domain),
     trägt es dort ein, **an beiden Stellen**.
   - Bei GitHub läuft dieselbe Prüfung als Action bei jedem Push und wöchentlich.
     Die Ausgabe nennt nur Datei und Zeile, nie den Treffer.

**Ausnahme:** `LICENSE`, `LICENSE-CODE` und `NOTICE` nennen den Rechteinhaber absichtlich
mit Namen und sind vom Namens-Scan ausgenommen. Sonst steht der Name nirgends; auch nicht
in Kapiteln, der README oder Commit-Botschaften.

Was einmal gepusht ist, bleibt in der Git-Historie. Ein nachträgliches Löschen schützt
nicht mehr.

## Konventionen

- Deutsch, Ordnernamen `klein-mit-bindestrich`, Umlaute ausgeschrieben.
- Neues Kapitel → Zeile in der Kapitel-Tabelle der [`README.md`](README.md).
- Befund vor Empfehlung, Begründung zu jeder Regel, Grenzen ausdrücklich benennen.
- Direkt auf `main`; Commit-Botschaft nennt das Werkzeug (`@claude`, `@codex`).
