---
stand: 2026-10-12
fassung: 2
---

# Bauanleitung: Mehrere KI-Sitzungen über viele Repositories koordinieren

> **Für wen diese Datei ist:** für eine KI (z. B. einen Coding-Assistenten mit
> Shell-Zugriff), die gemeinsam mit einem Menschen eine Arbeitsumgebung aufbauen soll, in
> der **mehrere KI-Sitzungen**, womöglich **mehrere Werkzeuge** (zwei verschiedene
> Assistenten) und **viele Repositories** nebeneinander existieren — auf einem Rechner,
> teils gleichzeitig. Der Mensch hat so etwas vielleicht noch nie gemacht.
>
> **Wie du sie nutzt:** Lies die Datei ganz, bevor du etwas tust. Arbeite die Phasen in
> der angegebenen Reihenfolge ab. Passe alles an die tatsächliche Umgebung an und
> **übernimm nichts blind**. Hier stehen Muster, Begründungen und Beispielwerte, keine
> fertigen Einstellungen.
>
> Alle Namen in `<spitzen Klammern>` sind Platzhalter, die du mit dem Nutzer festlegst.
> `<projekte>/` ist der Ordner, unter dem alle Repositories liegen; `<admin-repo>` ist
> das eine Repository darin, das für alle anderen gilt; `<regeldatei>.md` ist die
> Anweisungsdatei, die dein Werkzeug in einem Projekt liest (der Name hängt vom Werkzeug
> ab, siehe Abschnitt 2).
>
> **Alle Shell-Beispiele setzen eine Unix-Shell voraus** (bash oder zsh auf macOS oder
> Linux). Unter Windows mit PowerShell gelten andere Expansions- und Signalregeln; die
> Wächter 2 und 3 aus Abschnitt 3 müssen dort neu gedacht werden, nicht übersetzt.

> **Woher das kommt:** Jede Regel hier ist aus einem Fehler entstanden, der in einer
> solchen Umgebung tatsächlich passiert ist — nicht aus Systematik. Wo eine Regel einen
> Mechanismus hat, steht er daneben; wo sie nur Text ist, steht, warum das nicht reicht.
> Zahlen aus einer konkreten Umgebung fehlen absichtlich; sie würden nur so tun, als
> gälten sie auch für deine.

### Wie verbindlich ist ein Abschnitt?

| Kennzeichnung | Bedeutung |
|---|---|
| **[Pflicht]** | Ohne das funktioniert der Rest nicht oder wird gefährlich |
| **[je nach Werkzeug]** | Hängt davon ab, was die eingesetzten Assistenten an Hooks, Fertigkeiten und Konfiguration bieten. Der Abschnitt nennt jeweils, was ohne diese Möglichkeit bleibt |
| **[Option]** | Lohnt sich, sobald die Pflichtteile stehen |

---

## 0. Das Problem, das hier gelöst wird [Pflicht]

Eine KI-Sitzung ist ein Kurzzeitgedächtnis mit Shell-Zugriff. Sie weiß nur, was in ihrem
Kontext steht, und sie ist weg, wenn das Fenster zugeht. Solange ein Mensch mit **einer**
Sitzung in **einem** Repository arbeitet, trägt er das Gedächtnis selbst. Ab dem zweiten
Werkzeug und der zweiten gleichzeitigen Sitzung geht das schief, und zwar auf immer
dieselben Weisen:

- **Zwei Wahrheiten.** Jedes Werkzeug hat seine eigene Anweisungsdatei. Wer eine Regel in
  der einen ändert, vergisst die andere. Nach einem Monat widersprechen sie sich, und
  keine Sitzung merkt es.
- **Raten statt wissen.** Eine Sitzung hält den Rechner für ein anderes Betriebssystem,
  sucht Zugangsdaten, die woanders liegen, oder bindet im CI einen festen Port auf einem
  Runner, den sich mehrere Repositories teilen — obwohl jede dieser Antworten irgendwo
  zentral steht. Sie steht nur nicht **dort, wo die Sitzung hinsieht**.
- **Befunde sterben im Agentenspeicher.** Eine Sitzung lernt etwas Wichtiges, legt es in
  ihren eigenen Speicher (eine Datei, die nur dieses Werkzeug liest) — und die nächste
  Sitzung des anderen Werkzeugs lernt es neu.
- **Parallele Sitzungen räumen einander ab.** Ein `git add -A` nimmt die uncommittete
  Arbeit der Nachbarsitzung mit. Ein `pkill` mit einem Muster trifft den fremden Server.
  Zwei Entwicklungsserver auf einem Build-Verzeichnis zerstören sich den Zwischenspeicher.
- **Dieselbe Frage, zweimal beantwortet.** Zwei Sitzungen stoßen auf dasselbe Problem und
  lösen es verschieden, weil es keinen Ort gibt, an dem eine Entscheidung für alle gilt.
- **Löschen mit leerer Variable.** `rm -rf $VERZ/*` mit einem `$VERZ`, das in diesem
  Aufruf nie gesetzt wurde, ist `rm -rf /*`. Das ist in der Praxis passiert, im
  Aufräumteil einer Sitzung — und die Sitzung **kannte** die Regel dagegen.

Die letzte Zeile ist der Schlüssel zu allem Weiteren: **Regeln, die nur Text sind,
verlieren.** Was nicht als Mechanismus greift, wird irgendwann von einer Sitzung
ignoriert, die es besser wusste. Diese Anleitung baut deshalb an jeder Stelle, wo es geht,
einen Mechanismus — und benennt ehrlich, wo es nicht geht.

**Vier Grundsätze**, die in allen Abschnitten wiederkehren:

1. **Das Repository ist die Dokumentation. Anweisungsdateien sind Türen.** Geschrieben
   wird an genau einer Stelle; die Tür ist so dünn wie möglich.
2. **Mechanismus vor Prosa.** Ein Hook, der einen Befehl ablehnt, ist mehr wert als ein
   Absatz, der davor warnt. Wo beides existiert und sich widerspricht, gewinnt der
   Mechanismus — und der Text wird korrigiert.
3. **Wissen wird geliefert, nicht hingelegt.** Was eine Sitzung wissen muss, steht in der
   Datei, die sie ohnehin liest — nicht in einem Dokument, das sie suchen müsste.
4. **Befund vor Empfehlung.** Erst was gemessen wurde, dann was daraus folgt. Zahlen
   werden ausgezählt, nicht überschlagen. Ein leeres Suchergebnis bestätigt nichts.

---

## 1. Die Landkarte: ein Verwaltungs-Repository neben den Projekten [Pflicht]

```
<projekte>/
  <admin-repo>/        gilt für alle Projekte: Regeln, Vorgaben, Rückkanal, Prüfskripte
  <projekt-a>/         ein Produkt, ein Repository
  <projekt-b>/
  …
```

Das `<admin-repo>` hält **keinen Code und keine Zugangsdaten**, nur Dokumentation und ein
paar Prüfskripte. Es ist **privat**: Es nennt Rechner, Runner, Pfade und Projekte beim
Namen. Was hineingehört, entscheidet eine einzige Frage: **Wäre die Aussage auf einem
neuen Rechner noch wahr?** Dann gehört sie hierher. Betrifft sie nur diese Maschine
(installierte Werkzeuge, lokale Pfade, Zeitpläne), gehört sie in ein eigenes
Rechner-Repository; betrifft sie nur Server, in ein Server-Repository. Die drei bleiben
getrennt, weil ihre Gültigkeitsbereiche verschieden alt werden.

Im `<admin-repo>` liegen fünf Dinge:

| Ordner | Inhalt | Abschnitt |
|---|---|---|
| `global/` | der **Kanon** der Regeln und alles, was daraus in die Werkzeug-Homes ausgerollt wird: Fertigkeiten, Hooks, Regelteile von Konfigurationsdateien | 2, 3 |
| `docs/` | Vorgaben mit Begründung, Verfahren, Messungen über alle Projekte | 5, 9 |
| `feedback/` | der **Rückkanal**: eine Datei je Projekt | 6 |
| `register/` | die zentrale Abschrift jedes Steckbriefs, zum Abgleich gegen die Projekte | 4 |
| `scripts/` | Steckbrief-Generator, Konformitäts-Check, Sync, Bestandszähler | 4, 9 |

Eine Regel, die an zwei Stellen steht, ist manchmal nötig. An drei Stellen nie: die
dritte Kopie ist immer die, die zuerst veraltet.

---

## 2. Ein Kanon, mehrere Türen [Pflicht, je nach Werkzeug]

Jedes Werkzeug liest beim Start eine globale Anweisungsdatei aus seinem Home-Verzeichnis
(etwa `~/.<werkzeug-a>/<anweisungen>.md`) und eine je Projekt im Repository. Zwei
Werkzeuge heißen zwei globale Dateien. Wer beide von Hand pflegt, hat nach kurzer Zeit zwei
Wahrheiten.

**Die Lösung ist eine Richtung:** Der Kanon liegt **einmal** im `<admin-repo>` unter
`global/regeln.md`. Die Dateien in den Werkzeug-Homes sind **Ausrollziele** — erzeugt, nicht
geschrieben. Ein Skript vergleicht Kanon und Ziele über Prüfsummen und kennt drei Zustände:

| Zustand | Bedeutung | Was das Skript tut |
|---|---|---|
| gleich | alle Ziele entsprechen dem Kanon | nichts |
| Drift | ein Ziel weicht vom Kanon ab | `--push` überschreibt es aus dem Kanon. `--pull <werkzeug>` holt die Änderung in den Kanon — **mit Angabe, aus welchem Ziel**, denn mit mehreren Zielen wäre ein blankes „pull" eine stille Wahl zwischen Wahrheiten; danach `--push`, damit alle Ziele wieder gleich sind |
| **Konflikt** | mindestens zwei Ziele weichen vom Kanon ab **und** voneinander | meldet, rollt **nichts** aus. Das ist der einzige Zustand, in dem keine Richtung offensichtlich ist; der Mensch entscheidet |

Dieselbe Mechanik gilt für alles, was in jedes Home gehört: **Fertigkeiten** (wiederverwendbare
Abläufe, die der Mensch per Befehl auslöst, etwa „Sitzung sauber beenden" — manche Werkzeuge
nennen sie Skills oder Slash-Befehle), **Hooks** (Abschnitt 3) und die **Regelteile von
Konfigurationsdateien**. Bei Konfigurationsdateien, die das Werkzeug auch selbst beschreibt,
wird **gemergt, nicht ersetzt**: nur die Schlüssel, die der Kanon kennt, werden verglichen
und gesetzt. Dazu zählt die **Registrierung der Hooks** — ein Hook wirkt erst, wenn die
Einstellungsdatei des Werkzeugs ihn für das richtige Ereignis nennt. Genau dieser Eintrag ist
Teil des Kanons, sonst liegt das Skript im Home und läuft nie.

Im Kanon selbst steht ganz oben ein Satz wie:

> *Kanon ist `<admin-repo>/global/regeln.md`. Die Dateien in den Werkzeug-Homes sind
> Ausrollziele — was dort direkt geändert wird, ist beim nächsten Abgleich wieder weg.*

Damit weiß jede Sitzung, die die ausgerollte Datei liest, wo sie ändern muss.

**Auf Projektebene gilt dasselbe, nur schärfer: genau eine Regeldatei je Repository.**
Nicht eine je Werkzeug. Drei Wege, je nachdem, was die Werkzeuge können:

1. **Konfigurierbarer Dateiname.** Manche Assistenten lassen sich einstellen, welche
   Datei sie im Projekt als Anweisung lesen; der zweite liest dann die Datei des ersten.
2. **Symlink.** Liest ein Werkzeug nur einen festen Dateinamen, zeigt eine Verknüpfung
   unter diesem Namen auf die eine Regeldatei. Ein Link ist keine zweite Wahrheit; die
   Prüfung in Abschnitt 9 erlaubt ihn ausdrücklich.
3. **Gar nicht.** Bleibt nur eine echte zweite Datei, ist sie **erzeugt** (aus der ersten,
   per Sync wie der Kanon) und trägt im Kopf den Satz, dass sie es ist.

Eine zweite, **von Hand geschriebene** Datei daneben heißt zwei Wahrheiten, und die zweite
veraltet zuerst. Die Namen solcher Dateien wechseln mit den Produkten (`AGENTS.md`,
`.cursorrules`, …); die Regel ist produktunabhängig. **Kein `init`-Befehl eines Werkzeugs**
darf eine solche Datei anlegen — er füllt sie mit generischem Inhalt, der vom ersten Tag an
von der ersten Datei abweicht. Wo ein Repository eine fremde Agentendatei aus einem Upstream
erbt, bleibt sie unangetastet und wird in der Prüfung als bekannte Ausnahme geführt.

Was in die Regeldatei gehört: Projektübersicht, Architekturprinzipien, Konventionen, die
Befehle (Test, Build, Deploy), Verweise in die Dokumentation — und der Steckbrief aus
Abschnitt 4. Was **nicht** hineingehört: Statusnotizen, offene Punkte, Sitzungsprotokolle.
Dafür gibt es Abschnitt 5.

---

## 3. Mechanismen statt Prosa: drei Wächter [Pflicht, je nach Werkzeug]

Manche Coding-Assistenten bieten **Hooks**: kleine Programme, die vor jedem Werkzeugaufruf
(etwa jedem Shell-Befehl) laufen, den geplanten Aufruf als Eingabe bekommen und ihn mit
einem Rückgabewert ablehnen können. Dort gehören die Regeln hin, deren Verletzung nicht
rückgängig zu machen ist. Drei haben sich als unverzichtbar erwiesen; jede ist aus einem
konkreten Schaden entstanden.

**Hat ein Werkzeug keine Hooks**, bleibt die Regel Prosa im Kanon — und das wird als Risiko
benannt, nicht verschwiegen. Ein teilweiser Ersatz ist ein Shell-Wrapper für `git` und `rm`
im Profil, das dieses Werkzeug benutzt; er fängt die einfachen Formen, nicht alle.

### Wächter 1: kein Sammel-Stagen

`git add -A`, `git add .`, `git add -u` und `git add <verzeichnis>/` nehmen **alles** mit,
was im Arbeitsbaum darunter liegt — auch die uncommittete Arbeit einer parallelen Sitzung,
die davon nichts weiß. Erlaubt sind nur **explizite Dateipfade**, die zur eigenen Aufgabe
gehören. Ein Pfad, der noch nicht existiert, ist eine neue Datei und bleibt erlaubt.

Warum ein Hook, obwohl das Werkzeug eine Verbotsliste für Befehle hat: solche Listen sind
meist **Präfix-Vergleiche** über die Kommandozeile. Sie fangen die aufgezählten
Schreibweisen und sonst nichts — `git -C <pfad> add -A` rutscht durch. Der Hook zerlegt den
Befehl und prüft die Argumente, egal wie sie geschrieben sind.

### Wächter 2: kein Löschen mit ungesichertem Pfad

```bash
rm -rf "${VERZ:?}"/*     # richtig: bricht ab, wenn VERZ leer ist
rm -rf $VERZ/*           # falsch: wird mit leerem VERZ zu  rm -rf /*
rm -rf "${VERZ:-/tmp}"/* # falsch: ein Vorgabewert verdeckt den Fehler doppelt
```

Zwei Tatsachen machen den zweiten Fall wahrscheinlicher, als er aussieht:

- **Umgebungsvariablen überleben keinen Werkzeugaufruf.** Zwischen zwei Shell-Aufrufen
  einer KI-Sitzung bleibt in der Regel nur das Arbeitsverzeichnis erhalten. `VERZ=…` im
  einen Aufruf und `rm -rf $VERZ/*` im nächsten ist ein `rm -rf /*`. Deshalb: **die
  Variable wird im selben Aufruf gesetzt, in dem sie benutzt wird.**
- **Aufräumen am Ende ist der gefährlichste Moment.** Die Sitzung ist fast fertig, der
  Kontext ist voll, die Sorgfalt ist aufgebraucht.

**Die Grenze von `:?`:** Es fängt nur die **leere** Variable. `VERZ=/` oder `VERZ=$HOME` mit
`:?` ist weiterhin `rm -rf /*`. Gegen einen **falschen** Wert hilft erst eine Prüfung des
Inhalts — `[[ "$VERZ" == "$SCRATCH"/* ]] || exit 1` vor dem Löschen — oder der Hook: Er
lehnt `rm`, `mv` und `rsync --delete` ab, wenn ein Zielpfad eine ungesicherte Expansion
enthält (`$VAR`, `${VAR}`, `${VAR:-…}` ohne `:?`) oder auf `/`, das Home-Verzeichnis oder
eine Ebene darunter zeigt. **Prüfe, ob dein Werkzeug Hooks auch in einem Modus mit
erweiterten Rechten ausführt** — genau dort braucht man ihn.

Dazu gehört die Regel, was überhaupt gelöscht werden darf: **Was dieser Lauf selbst
erzeugt hat** (Temp-Dateien, Zwischenstände, eigene Testlogs), ohne Rückfrage. **Was vor
der Sitzung da war** (Daten, Dateien, Ordner, Backups, fremde Arbeitsbaum-Änderungen),
nur nach Rücksprache — auch „leere" Ordner und „alte" Einträge. Statt löschen: markieren,
verschieben, deaktivieren. **„Aufräumen" heißt nicht löschen, sondern korrekt
einsortieren.** Fehlt eine Datei, auf die ein Datensatz zeigt, wird der Datensatz als
„fehlt" markiert, nicht entfernt.

### Wächter 3: Prozesse über die PID, nicht über ein Muster

```bash
pid=$(lsof -nP -iTCP:<port> -sTCP:LISTEN -t)   # leer oder mehrere Zeilen: anhalten, nicht raten
ps -p "$pid" -o pid,command                      # hinsehen, BEVOR das Signal geht
kill "$pid"
```

Auf minimalen Linux-Systemen fehlt `lsof`; dort liefert `ss -ltnp` den Prozess zum Port.
Bei **null** Treffern oder **mehreren** (ein Cluster, mehrere Worker) bricht die Folge ab,
statt zu töten: Mehrere PIDs in einer Variablen sind ein Argument mit Zeilenumbruch, und
genau dann wäre der fremde Server unter den Treffern.

`pkill -f "<muster>"` trifft, was dem Muster entspricht — **und mehr**. Auf Systemen mit
BSD-`getopt` (macOS, die BSDs) kommt eine Eigenheit dazu, die man dem Befehl nicht ansieht:
**das Muster muss zuletzt stehen.** Steht nach dem Muster noch eine Option, hört der Parser
beim ersten Nicht-Options-Argument auf — das Muster wird ignoriert, und das letzte Argument
wird zum Muster. `pkill -f "<muster>" -P 1` bedeutet dann `pkill -f 1`: ein Signal an jeden
Prozess, dessen Kommandozeile irgendwo eine `1` enthält. GNU-`getopt` (Linux) sortiert
Argumente um; dort ist dieselbe Zeile korrekt. Die portable Regel lautet deshalb **Optionen
immer vor das Muster** — sie wirkt auf beiden Systemen gleich. Ein Hook, der die falsche
Reihenfolge ablehnt, ist auf macOS Pflicht; auf Linux meldet er sie besser als Hinweis, sonst
produziert er dort den Fehlalarm, vor dem der nächste Abschnitt warnt.

Und: **Ausprobieren immer mit `pgrep`, nie mit `pkill`** — derselbe Parser, keine Wirkung.
Danach **hinsehen**: Eine leere Prozessliste nach dem Töten beweist nicht, dass nur der
eigene Prozess weg ist. Sie widerspricht höchstens.

### Wie ein Hook aussieht

Der Rahmen ist bei allen drei Wächtern gleich; nur die Prüfung unterscheidet sich. **Zwei
Dinge sind werkzeugabhängig** und stehen in dessen Dokumentation: die Form, in der der
geplante Aufruf übergeben wird (hier als Beispiel: JSON auf der Standardeingabe mit
Werkzeugname und Befehlstext; andere übergeben eine Argumentliste), und das Signal, mit dem
eine Ablehnung erwartet wird (hier: Rückgabewert 2 und eine Meldung auf der Fehlerausgabe).
Der Entwurf unten ist für Wächter 1 vollständig und getestet (Python ≥ 3.10); für die
anderen beiden tauschst du `befund()` aus.

```python
#!/usr/bin/env python3
"""Vor jedem Shell-Aufruf: kein Sammel-Stagen (git add -A / . / <verzeichnis> / Glob).
Warum es diesen Waechter gibt: ein Sammel-Stagen nimmt die uncommittete Arbeit einer
parallelen Sitzung mit, die davon nichts weiss. Verbotslisten des Werkzeugs sind
Praefix-Vergleiche und fangen `git -C <pfad> add -A` nicht.
Testen (in beide Richtungen, Python >= 3.10):  python3 waechter_stagen.py --test
"""
import json, re, shlex, sys

SHELL_WERKZEUG = "<name des shell-werkzeugs>"   # steht in der Doku deines Assistenten

def befehl_aus(eingabe: dict) -> str:
    # Die Form der Eingabe ist werkzeugabhaengig: manche uebergeben ein JSON mit dem
    # Befehlstext, andere eine Argumentliste. Hier anpassen, sonst prueft der Waechter nichts.
    return eingabe.get("tool_input", {}).get("command", "")

def segmente(befehl: str) -> list[list[str]]:
    """Zerlegt an && || ; | und tokenisiert jedes Stueck. Ab einem Heredoc-Start wird
    abgeschnitten: dessen Inhalt ist Text, kein Befehl."""
    befehl = re.split(r"<<-?\s*['\"]?\w+", befehl, maxsplit=1)[0]
    out = []
    for t in re.split(r"\s*(?:&&|\|\||;|\|)\s*", befehl):
        try:
            out.append(shlex.split(t))
        except ValueError:          # unpaarige Anfuehrungszeichen: grob tokenisieren
            out.append(t.split())
    return out

def befund(befehl: str) -> str | None:
    """Begruendung, wenn der Befehl abgelehnt werden muss - sonst None."""
    for tok in segmente(befehl):
        j = 0                                                  # fuehrende VAR=wert, sudo, env, time ueberspringen
        while j < len(tok) and (re.match(r"^\w+=", tok[j]) or tok[j] in ("sudo", "env", "time", "command", "nohup")):
            j += 1
        if j >= len(tok) or tok[j] != "git":                   # `git` muss der Befehl sein, nicht ein Wort darin
            continue
        i = j + 1
        while i < len(tok) and tok[i].startswith("-"):       # git -C <dir> / -c k=v / --no-pager
            i += 2 if tok[i] in ("-C", "-c") else 1
        if i >= len(tok) or tok[i] not in ("add", "stage"):
            continue
        for a in tok[i + 1:]:
            if a == "--":
                continue
            if a in ("--all", "--update", "--no-ignore-removal", "--ignore-removal"):
                return f"Sammel-Stagen ({a})"
            if a.startswith("-") and not a.startswith("--") and set(a[1:]) & set("Au"):
                return f"Sammel-Stagen ({a})"
            if a in (".", ":/") or a.endswith("/") or any(c in a for c in "*?["):
                return f"'{a}' nimmt alles darunter mit"
    return None

if __name__ == "__main__":
    if "--test" in sys.argv:
        muss_ab = ["git add -A", "git -C /x add .", "git add docs/", "git stage -Av", "git add -u",
                   "cd y && git add *", "git add -- .", "git add ':/'"]
        muss_durch = ["git add src/a.py docs/b.md", "git commit -m 'add -A'", "git status && ls -A",
                      "git add -p src/a.py", "echo git add . >> notiz.txt", "cat <<'EOF' > f\ngit add .\nEOF"]
        fehler = [b for b in muss_ab if not befund(b)] + [b for b in muss_durch if befund(b)]
        print("FEHLER:" if fehler else "ok -", fehler or f"{len(muss_ab)} abgelehnt, {len(muss_durch)} durchgelassen")
        sys.exit(1 if fehler else 0)
    try:
        eingabe = json.load(sys.stdin)
    except ValueError:
        # Unlesbare Eingabe: geschlossen versagen. Ein Waechter, der bei Stoerung durchlaesst,
        # schuetzt genau dann nicht, wenn etwas Unerwartetes passiert.
        print("ABGELEHNT: Eingabe unlesbar", file=sys.stderr); sys.exit(2)
    if eingabe.get("tool_name") != SHELL_WERKZEUG:
        sys.exit(0)                                           # kein Shell-Aufruf: nicht zustaendig
    grund = befund(befehl_aus(eingabe))
    if grund:
        print(f"ABGELEHNT: {grund}. Nur explizite Pfade stagen.", file=sys.stderr)
        sys.exit(2)                                           # Ablehnsignal: siehe Doku des Werkzeugs
```

Vier Entscheidungen in diesem Rahmen, die leicht übersehen werden:

- **Der Hook prüft, ob er zuständig ist** (`tool_name`). Registriert für alle
  Werkzeugaufrufe, liefe er sonst für jeden Datei-Edit mit.
- **Er versagt geschlossen.** Unlesbare Eingabe heißt Ablehnung, nicht Durchlassen. Ein
  Wächter, der bei Störung aufmacht, schützt genau dann nicht, wenn etwas Unerwartetes
  passiert.
- **Er zerlegt statt zu suchen.** Ein Regex über die ganze Zeile hätte `git commit -m 'add
  -A'` abgelehnt und `git add docs/` durchgelassen — der Wächter, den man wegklickt. Der
  Entwurf zerlegt an `&&`, `;`, `|`, schneidet Heredoc-Inhalt ab (Text, kein Befehl) und
  prüft nur Segmente, deren Befehlswort `git` ist.
- **Er trägt seine Tests in sich.** `--test` prüft Fälle, die er ablehnen muss, **und**
  Fälle, die er durchlassen muss. Vor jedem Ausrollen laufen beide.

**Jeder Hook trägt im Kopf, warum es ihn gibt** — den Vorfall, nicht die Regel. Die Regel
steht im Kanon; der Vorfall erklärt der nächsten Sitzung, warum sie ihn nicht abschalten
sollte. Die Skripte liegen in `<admin-repo>/global/hooks/`; der Sync aus Abschnitt 2
kopiert sie in jedes Home, setzt sie ausführbar und trägt die Registrierung in die
Einstellungsdatei des Werkzeugs ein.

Teste jeden Wächter mit den Formen, die Sitzungen tatsächlich schreiben: Heredocs,
mehrzeilige Befehle, `git -C`, verkettete Befehle, ein Befehlswort als bloßer Text in
einem `echo`. Eine grüne Falltabelle prüft, wie **du** testest, nicht wie Sitzungen
arbeiten.

---

## 4. Der Steckbrief: Fakten liefern, statt sie suchen zu lassen [Pflicht]

Die teuersten Fehler einer Sitzung sind Annahmen über Dinge, die irgendwo feststehen: Auf
welchem Betriebssystem laufe ich? Wie wird dieses Projekt ausgeliefert, und ist das je
gelaufen? Wo liegen die Zugangsdaten? Welche Ports sind lokal und im CI belegt — und teilt
sich der CI-Runner mit anderen Repositories? Wie viel Arbeitsspeicher hat der Rechner, und
wie viel davon ist einer Container-VM fest zugesagt?

Diese Antworten stehen nicht in der Dokumentation des Projekts, weil sie
**projektübergreifend** sind. Sie stehen auch nicht zuverlässig im Gedächtnis des Menschen.
Sie gehören in die eine Datei, die jede Sitzung sicher liest: die Regeldatei des Projekts
— als **erzeugter Block** zwischen zwei Markern.

```markdown
<!-- STECKBRIEF:BEGIN (erzeugt, nicht von Hand aendern) -->
| | | Herkunft |
|---|---|---|
| **Dieser Rechner** | <OS> <Architektur> - läuft hier nicht: <fehlende Werkzeuge> | gemessen |
| **Arbeitsspeicher** | <gesamt> · Container-VM dauerhaft zugesagt: <RAM + Swap> | gemessen |
| **Hauptbranch** | `<branch>` | gemessen |
| **Laufzeit-Pin** | <Pin-Datei der Toolchain, z. B. für Node oder Python, oder —> | gemessen |
| **CI läuft auf** | <Anbieter-Runner (frische VM je Job) / eigener Runner, geteilt mit …> | gemessen (CI-API) |
| **Deploy-Weg** | <Skript oder Workflow> | zentral festgehalten |
| **— Zustand** | <✅ gelaufen am … / ⚠️ nie belegt> | zentral festgehalten + gemessen |
| **Zugangsdaten liegen** | <Dateien, Variablen-NAMEN - nie Werte> | gemessen |
| **Host-Ports lokal** | <aus Compose-Dateien gemessen> | gemessen |
| **Host-Ports im CI** | <aus Workflows gemessen; fest oder dynamisch?> | gemessen |
<!-- STECKBRIEF:END -->
```

Die Regeln dazu:

- **Er wird erzeugt, nicht geschrieben.** Ein Skript im `<admin-repo>` misst, was messbar
  ist (aus Compose-Dateien, Workflows, der CI-API, dem System), und liest, was nur zentral
  festgehalten werden kann (etwa den beschlossenen Deploy-Weg), aus einer Tabelle in dessen
  `docs/`. **Die Spalte „Herkunft" steht im Block**, damit eine Sitzung weiß, ob sie einer
  Messung oder einer Festlegung gegenübersteht. Eine Abschrift je Projekt liegt zusätzlich
  unter `register/`, damit die Prüfung (Abschnitt 9) Abweichungen zwischen beiden sieht.
- **Niemand ändert ihn von Hand im Projekt.** Stimmt eine gemessene Zeile nicht, ist die
  **Messung** falsch — dann wird das Skript korrigiert. Stimmt eine festgehaltene Zeile
  nicht, wird die zentrale Tabelle korrigiert. In beiden Fällen nicht der Block: Der nächste
  Lauf überschriebe die Korrektur, und der Fehler käme zurück.
- **Ein `—` heißt „nicht messbar", nicht „gibt es nicht".** Es ist ein Ergebnis, keine
  Lücke zum Auffüllen.
- **Zugangsdaten nur als Namen.** Welche Datei, welche Variablen — nie ein Wert. Und auch
  die Namen nur, wenn die Regeldatei in einem **privaten** Repository liegt. In einem
  öffentlichen Repository ist schon der Pfad zur Token-Datei ein Hinweis für Angreifer; dort
  entfällt die Zeile, und der Steckbrief insgesamt wird knapper.
- **Lauf immer mit Projektfilter.** Ohne ihn schreibt das Skript in alle Repositories —
  auch in die, in denen gerade eine andere Sitzung arbeitet, und in deren Worktrees. Die
  finden dann „fremde Änderungen" vor. Der filterlose Lauf gehört dem wöchentlichen
  Prüflauf (Abschnitt 9).
- **Die Speicherzeile ist eine Rechenaufgabe, keine Zierde.** Wer viele Prozesse parallel
  startet, misst **einen** davon (in Python etwa über `resource.getrusage`), multipliziert
  mit der Anzahl und hält das gegen Gesamtspeicher minus VM-Zusage. Arbeitsspeicher ist
  eine geteilte Ressource wie Host-Ports — nur bricht die Kollision nicht einen Job ab,
  sondern die Maschine.

Im Kanon steht dazu ein Satz, der der Sitzung die Reihenfolge vorgibt: **Lies den
Steckbrief, bevor du eine Annahme bildest.** Und: Wer einen projektübergreifenden Fakt
festhält, prüft zuerst, ob er in den Steckbrief gehört — und trägt ihn dann dort ein (im
Skript oder in der zentralen Tabelle), nicht in einen neuen Absatz irgendwo unter `docs/`.

---

## 5. Offener Bestand je Projekt: fünf Dateien, IDs, Schreiber-Tag [Pflicht]

Jedes Projekt sammelt, was offen ist — Fehler, Aufgaben, Ideen, Fragen. Ohne Vorgabe
entstehen dafür in jedem Repository andere Dateien, mit Datum im Namen, die beerbt statt
fortgeschrieben werden; nach einigen Monaten liegen in einem Projekt mehrere Listen, und
niemand weiß, welche gilt. Die Vorgabe ist deshalb **in jedem Projekt derselbe Baum**:

```
README.md · <regeldatei>.md      Pflicht. Sonst nichts Eigenes im Wurzelverzeichnis
docs/index.md                    Pflicht. Einstieg: was liegt wo
docs/offen/                      Pflicht. Die Arbeit (unten)
docs/offen/grossunterfangen/     Nach Bedarf. Große Vorhaben (unten) - der einzige Unterordner
docs/01-architektur/  02-fachlichkeit/  03-entwicklung/  04-daten/
docs/05-sicherheit/   06-betrieb/       07-pruefung/     08-entscheidungen/
docs/archiv/                     Zeitdokumente: abgeschlossen, wird nicht fortgeschrieben
```

**Weglassen ja, umbenennen nein, erfinden nein.** Die Liste ist geschlossen. Ein Bereich
ohne Inhalt wird nicht angelegt; aber er wird auch nicht anders benannt, und ein neunter
Bereich wird nicht erfunden. Jede Datei unter `docs/` beginnt mit drei Zeilen — `stand:`,
`geprueft_gegen:`, `status:` (`gueltig | entwurf | zeitdokument | ueberholt`) — und
`geprueft_gegen` bleibt leer, wenn nicht geprüft wurde. Erfunden ist schlimmer als leer.

### `docs/offen/` — eine Datei je Art

| Datei | Inhalt | Präfix der IDs |
|---|---|---|
| `fehler.md` | beobachtetes Fehlverhalten, mit Reproduktionsweg | `FE` (Fehler) |
| `aufgaben.md` | beschlossene, noch nicht gebaute Arbeit | `AU` (Aufgabe) |
| `ideen.md` | nicht beschlossen — nur notiert | `ID` (Idee — das Kürzel kollidiert mit dem Wort „ID"; es ist trotzdem gewählt, weil es im Satz „`ID4` aus `ideen.md`" eindeutig bleibt) |
| `fragen.md` | wartet auf eine Entscheidung, nicht auf Arbeit | `FR` (Frage) |
| `erledigt.md` | Abgehaktes, mit Datum, Commit und Werkzeug | behält die ID des Eintrags |

- **Kein Datum im Dateinamen, keine Sitzungsdatei, keine Statusnotiz in der Regeldatei.**
- **Erledigtes verlässt die Arbeitsdatei vollständig** und wandert nach `erledigt.md`.
  Kein Grabstein: kein `- [x]`, keine durchgestrichene Zeile, kein „siehe erledigt". Die
  Nummer bleibt vergeben, der Rest steht in der Git-Historie. Das **dauerhafte Ergebnis**
  gehört in die Fachdokumentation, nicht in die Liste.
- **Jeder Eintrag bekommt eine ID** und behält sie für immer: Präfix plus fortlaufende
  Nummer je Präfix. **Eine vergebene Nummer wird nie neu vergeben**, auch nach Erledigung
  nicht — sonst zeigt eine ältere Referenz irgendwann auf einen anderen Sachverhalt. Zieht
  ein Punkt in eine andere Liste um, wandert die ID mit.
- **Eine Prioritätsmarke steht zwischen Checkbox und ID:** 🔴 wirkt auf Auslieferung oder
  Datensicherheit oder scheitert still · 🟡 kostet beim nächsten Vorfall Zeit · ⚪ aufräumen,
  wenn man ohnehin in der Nähe ist · ⬜ kein Auftrag, sondern Kenntnisnahme. Die Skala ist
  Beispiel; wichtig ist, dass es **eine** gibt und der Zähler (Abschnitt 9) jede andere
  Marke meldet.
- **Wer etwas einträgt, nennt sich im Eintrag**, nicht nur in der Commit-Botschaft:
  hinter der ID steht das Schreiber-Tag, `@<werkzeug-a>`, `@<werkzeug-b>` oder `@mensch`.
  Die Commit-Botschaft nennt das Werkzeug zusätzlich; widersprechen sich zwei Aussagen,
  ist das die Spur zurück. In der Praxis nennt ohne diese Regel ein Großteil der Commits
  das Werkzeug gar nicht — deshalb gehört es in den Eintrag, wo es nicht vergessen wird.
- **Was eine Seite braucht, bevor jemand anfangen kann, ist kein Listeneintrag.** Es
  bekommt eine eigene Datei in `docs/offen/grossunterfangen/` mit sieben Abschnitten:
  Anlass · Gegenstand · Stand · Reichweite · Verworfen · Auslöser · Verlauf. `Verworfen`
  und `Auslöser` werden gern weggelassen und sind gerade deshalb Pflicht — sonst kommt ein
  verworfener Weg als frischer Vorschlag zurück, und ein Vorhaben ohne Endbedingung liegt,
  bis es niemand mehr anfasst.

### Zwei Rückmeldeschlitze je Eintrag

Jeder offene Eintrag endet mit zwei Zeilen:

```markdown
- [ ] 🟡 **AU7** `@<werkzeug-a>` — Titel …
  Beschreibung …
  - 💬 **User:** —
  - 🤖 **KI:** —
```

Der erste Schlitz gehört dem **Menschen**: Er hat das Dokument gelesen und etwas dazu
gesagt, **bevor** die nächste Sitzung begann. Der zweite gehört **anderen Sitzungen**:
Eine Sitzung des anderen Werkzeugs oder eines anderen Projekts kennt etwas, das hier
hilft, und trägt es mit Absender ein — dabei **ersetzt das Tag das Wort „KI"**:
`- 🤖 **@<werkzeug-b>:** In Projekt X dasselbe Muster, dort gelöst über …`

`—` heißt leer. **Ein gefüllter Schlitz hat Vorrang vor dem Eintrag selbst** und wird zu
Beginn jeder Sitzung gesucht — vom Wurzelverzeichnis des Projekts aus:

```bash
grep -rnE --exclude=README.md '^ *- (💬 \*\*User:\*\*|🤖 \*\*[^*]+:\*\*)' \
     docs/offen/ <admin-repo>/feedback/ \
  | grep -vE '^[^:]+:[0-9]+: *- (💬|🤖) \*\*[^*]+:\*\* *—? *$'
```

Der zweite Teil entfernt **genau die leere Form** (Schlitz, dann höchstens ein
Gedankenstrich) — nicht „alles, was auf einen Strich endet". Drei Fallen, alle in der Praxis
aufgetreten: **Nicht nach `🤖 **KI:**` suchen** — ein gefüllter Schlitz heißt nie mehr so,
weil der Schreiber das Wort ersetzt hat; eine frühere Fassung des Befehls fand damit keine
einzige der vorhandenen Rückmeldungen. **Nicht auf `—$` filtern** — das verwirft still jede
Rückmeldung, deren Text auf einen Gedankenstrich endet. **Nicht auf `\*\*$` filtern** — das
verwirft eine Rückmeldung, die mit einem fett gesetzten Verweis endet. Die Symbole sind
Beispiel: Jede eindeutige Marke tut es, auch ASCII; entscheidend ist, dass der Suchbefehl
**exakt dieselbe Form** benutzt wie die Einträge (Emoji haben Varianten, und das Terminal
braucht eine UTF-8-Locale).

**In den `💬`-Schlitz schreibt eine Sitzung nie.** Was sie daraus aufnimmt, wandert als
`**Rückmeldung (Datum):** …` in den Text des Eintrags; erst dann geht der Schlitz auf `—`
zurück. Spurlos löschen heißt, denselben Einwand beim nächsten Mal erneut zu bekommen.

---

## 6. Der Rückkanal zwischen den Repositories [Pflicht]

Zentrale Erkenntnisse sind wertlos, wenn sie die Projekte nicht erreichen. Ein Befund wie
*„von allen Deploy-Skripten überträgt genau eines wiederaufsetzbar"* steht in der Doku
des `<admin-repo>` — aber wer in Projekt A arbeitet, liest dieses Dokument nicht. Deshalb
gibt es je Projekt eine Datei `<admin-repo>/feedback/<projekt>.md`, in der derselbe Befund
als **eine Zeile für genau dieses Projekt** steht.

| Gehört in den Rückkanal | Gehört ins Projekt-Repository |
|---|---|
| Eine zentrale Regel, die dieses Projekt noch nicht erfüllt | Fachliche Aufgaben, Bugs, Features |
| Ein Befund aus einem **anderen** Projekt, der hier genauso gilt | Alles, was ohne zentrale Sicht sichtbar ist |
| Etwas, das nur im Vergleich über alle Projekte auffällt | |

Der Rückkanal ist **kein zweiter Backlog**. So sieht eine Datei im Kleinsten aus:

```markdown
# Feedback: <projekt>

Zentrale Sicht, Stand <datum>. Ablauf: README.md.

## Aufträge

- [x] ✅ **A1** `@<werkzeug-a>` — **Compose bindet Ports ohne 127.0.0.1.** — *erledigt <datum>, `<commit>`*
  - 💬 **User:** —
  - 🤖 **KI:** —

- [ ] 🟡 **A2** `@<werkzeug-a>` — **`.gitattributes` fehlt** — CRLF-Drift beim nächsten
  Kontakt mit einem anderen Betriebssystem. Vorlage: Projekt B, `<commit>`.
  - 💬 **User:** —
  - 🤖 **KI:** —

## Fragen an das Projekt

### ❓ F1 `@<werkzeug-a>` — Welche Node-Version soll gepinnt werden? · *Entscheidung*
Zwei Projekte pinnen 22, eines 20. Zentral nicht entscheidbar.

**💬 Antwort:** _(offen)_
  - 🤖 **KI:** —
```

Zwei Eintragsformen, mit Absicht: **Aufträge als Checkbox** (`- [ ] … **A<n>** …`), weil
sie kurz sind und abgehakt werden; **Fragen als Überschrift** (`### ❓ F<n> …`), weil ihre
Antwort lang wird und gegliedert sein will. Diese Mischung hat einen Preis, der weiter unten
steht. **Anders als in `docs/offen/` bleibt ein erledigter Auftrag hier als `✅` stehen:**
Die zentrale Seite muss sehen, dass die Frage gestellt **und** beantwortet wurde — sonst
stellt sie sie in drei Monaten neu. Erst ein zentrales Review räumt alte `✅` heraus.

### Schritt 1 jeder Sitzung

Im Kanon steht als erste Regel: **Die Feedback-Datei des Projekts wird gelesen und
abgearbeitet, bevor die eigentliche Aufgabe beginnt.** Nicht nebenbei, nicht am Ende. Der
Grund ist Reihenfolge: Ein Punkt, der zentral schon entschieden ist, würde sonst ein
zweites Mal erarbeitet — und eine offene Frage blockiert eine Entscheidung, die über alle
Projekte wirkt, solange sie unbeantwortet bleibt.

0. **Zuerst nachsehen, ob jemand etwas hineingeschrieben hat** (Suchbefehl in Abschnitt 5).
   Ein gefüllter Schlitz hat Vorrang.
1. **Durchgehen und einsortieren.** Kleine, zu hundert Prozent offensichtliche Punkte
   direkt umsetzen. Alles, was Fachlogik berührt oder eine Entscheidung des Projekts ist:
   fragen statt raten. Erledigtes als `✅` abhaken (Datum + Commit), nicht löschen. **Stimmt
   ein Punkt nicht, widersprechen** — als ❌ mit Begründung. Das ist ein Ergebnis, kein
   Versäumnis, und korrigiert die zentrale Sicht.
2. **Offene Fragen beantworten**, wo der Projektkontext es hergibt: Antwort in die Datei,
   mit Datum und Quelle. **Nichts erfinden** — unbeantwortet lassen ist ein Ergebnis.
3. **Erst dann die eigene Aufgabe.** Was länger dauert als ein paar Minuten, wird nicht
   stillschweigend vorgezogen: kurz melden, was dort liegt, und weitermachen. Verlangt der
   Mensch ausdrücklich zuerst etwas anderes, gilt das; die Datei ist dann spätestens beim
   Sitzungsende fällig.

### Fragen haben einen Lebenszyklus — und drei Regeln

```
### ❓ F3 — …     gestellt, wartet auf Antwort
### 💬 F3 — …     beantwortet, zentral noch nicht verarbeitet
### ✅ F3 — …     verarbeitet, mit Zeiger wohin
```

1. Eine Frage nennt, **wer** sie beantworten kann (Entscheidung des Menschen, Wissen des
   Projekts, Messung) — sonst wartet sie auf niemanden.
2. Die Antwort wird **verarbeitet**, nicht nur abgelegt: Die Entscheidung landet dort, wo
   sie gilt (Kanon, Vorgabe, Skript), und die Frage zeigt dorthin.
3. **Eine Frage, die zwei Reviews übersteht, ist falsch gestellt.** Sie wird vereinfacht,
   auf ein Ja/Nein gebracht oder geschlossen — nicht ein drittes Mal fortgeschrieben.

### Wer schreibt, liefert aus

- **Die schreibende Sitzung committet und pusht ihre Änderung im `<admin-repo>` selbst** —
  nur die eigenen Pfade, eigener Commit, auch wenn sie eigentlich in einem anderen Projekt
  arbeitet. Das `<admin-repo>` hat keinen Deploy; Ausliefern heißt dort `commit` + `push`,
  und dafür braucht es kein Projektwissen. Der Normalweg, weil mehrere Sitzungen in
  dasselbe Repository pushen und jeder zweite Push sonst abgelehnt wird:

  ```bash
  git -C <admin-repo> add feedback/<projekt>.md
  git -C <admin-repo> commit -m "feedback(<projekt>): A2 erledigt (@<werkzeug>)"
  git -C <admin-repo> pull --rebase && git -C <admin-repo> push
  ```

- **Uncommittet liegen lassen ist die einzige unzulässige Variante.** Die nächste Sitzung
  findet eine fremde Änderung vor und muss eine Rückfrage stellen, die sie nicht
  beantworten kann.
- **Ein Deploy wird nie von außen ausgelöst.** Eine Sitzung in Projekt A deployt weder
  Projekt B noch irgendetwas wegen einer zentralen Änderung.
- **Bricht der Rebase in einer fremden Datei ab: `git rebase --abort`, stoppen,
  berichten** — nicht fremden Inhalt auflösen. Mit zwei Werkzeugen und gleichzeitigen
  Sitzungen ist das der Punkt, an dem sonst still zwei Wahrheiten zusammengeführt werden.
- **Nächste Nummer = höchste vorhandene + 1, über beide Eintragsformen gesucht.** Das ist
  der Preis der Mischung von oben: Wer nur Checkboxen zählt, übersieht die Überschriften und
  vergibt eine Nummer doppelt. Eine Doppelung **in derselben Datei** ist statisch prüfbar
  (Abschnitt 9); dass eine Nummer nie wiederverwendet wird, ist es nicht. Ein Sammeleintrag
  über einen Bereich (`### ✅ A<n>–A<m>`) zählt dabei nicht als Vergabe von `A<n>`.

[je nach Werkzeug] Manche Assistenten dürfen nur im aktuellen Arbeitsverzeichnis
schreiben. Dann braucht der Rückkanal eine ausdrückliche Freigabe für den Pfad des
`<admin-repo>` in der Konfiguration des Werkzeugs — sonst kann die Sitzung Punkte
abhaken, aber nicht ausliefern, und stellt systematisch den verbotenen Zustand her.

---

## 7. Parallel arbeiten, ohne einander zu überschreiben [Pflicht]

Mehrere Sitzungen im selben Repository, teils ohne voneinander zu wissen, sind der
Normalfall, nicht die Ausnahme.

**Das erste Mittel ist Trennung, nicht Vorsicht:** Wenn das Werkzeug es kann, bekommt jede
Sitzung einen **eigenen Arbeitsbaum** (`git worktree add <pfad> -b <branch>`) oder
zumindest einen eigenen Branch. Dann gibt es keine fremde uncommittete Arbeit im eigenen
Baum, kein geteiltes Build-Verzeichnis und keinen Rebase in fremden Dateien. Die folgenden
Regeln gelten für den Fall, dass das nicht geht oder nicht geschehen ist — und sie wirken in
einer Einzelsitzung übertrieben, weil sie es dort auch sind:

- **Nur explizite Pfade stagen** (Wächter 1). Fremde Änderungen im Arbeitsbaum bleiben
  liegen und werden im Bericht genannt. Beim Ausliefern fragt die Sitzung **einmal**, ob
  fremde Änderungen mit sollen. Eine zweite Variante der Auslieferungs-Fertigkeit, die der
  Mensch ausdrücklich aufruft, nimmt den ganzen Arbeitsbaum mit — ohne Rückfrage, weil der
  Aufruf die Rückfrage ist.
- **Prozesse über die PID** (Wächter 3).
- **Zwei Entwicklungsserver auf einem Build-Verzeichnis zerstören sich den
  Zwischenspeicher.** Bei einem verbreiteten React-Framework antworten vorhandene Routen
  dann mit 404, im Log steht ein Modulfehler — das sieht nach kaputtem Router aus und ist
  keiner. Abhilfe ohne den fremden Prozess anzufassen: das Build-Verzeichnis über eine
  Umgebungsvariable umstellbar machen und mit eigenem Verzeichnis starten.
- **Der Agentenspeicher ist Arbeitsspeicher, kein Ablageort.** Was ein Werkzeug in seinen
  eigenen Speicher legt, ist maschinenlokal, unversioniert und für das andere Werkzeug
  unsichtbar — also weder auffindbar noch widerlegbar. Ein Befund gehört ins Repository, wo
  ihm jemand widersprechen kann.
- **Selbst testen mit eigenen Demo-Konten.** Jedes Projekt mit Anmeldung bekommt zwei
  bleibende Testkonten (Nutzer- und Adminrechte), an der Adresse erkennbar, lokal und auf
  der Zielumgebung. Geschrieben wird nur im eigenen Bereich des Demo-Kontos; das Admin-Konto
  **liest** fremde Daten, schreibt nicht. Zugangsdaten in `.env` oder einer Token-Datei
  mit Rechten `600`, nie im Repository.
- **Vor „läuft" steht ein Durchlauf durch die echte Oberfläche** — gesteuerter Browser, auf
  der Umgebung, über die die Aussage gemacht wird, in beiden Rollen. Grüne Unit-Tests
  belegen, dass die Annahmen des Tests zueinander passen, nicht dass ein Nutzer
  durchkommt. **Der Bericht nennt den Weg, nicht nur das Ergebnis:** geprüfter Ablauf,
  Umgebung, Konto. Was nicht geprüft wurde, wird als ungeprüft benannt.
- **Ports in Compose-Dateien an `127.0.0.1` binden** (`"127.0.0.1:5432:5432"`), Ausnahmen
  bewusst und je Zeile — etwa wenn eine Web-Oberfläche vom Handy erreichbar sein soll.
  Ohne Präfix sind Datenbank, Cache und Objektspeicher samt Entwicklungs-Zugangsdaten für
  jeden im selben Netz erreichbar; auf einem Laptop, der die Netze wechselt, ist das der
  Unterschied. **Die Host-Firewall ist hier nicht der Schutz:** Auf macOS reicht der
  Container-Dienst Ports über signierte Software durch, die die Anwendungsfirewall
  standardmäßig erlaubt; auf Linux schreibt Docker eigene Paketfilter-Ketten vor die
  üblichen Firewall-Regeln. Beides heißt: die Bindung ist der Schutz. Auf einem
  **geteilten** CI-Runner kommt dazu: feste Host-Ports in Workflows kollidieren zwischen
  Repositories, und das Symptom ist nicht „Port belegt", sondern ein Test, der eine
  **fremde Datenbank** erreicht. Ports im CI über eine Variable vergeben.

---

## 8. Ende der Sitzung: Review, Abgleich, Ausliefern [Pflicht, je nach Werkzeug]

Der Abschluss ist eine Fertigkeit (Abschnitt 2), die in jedem Werkzeug gleich heißt und
gleich läuft. Hat ein Werkzeug keinen Fertigkeiten-Mechanismus, steht die Abfolge als
Abschnitt im Kanon, und der Mensch löst sie mit „Sitzung beenden" aus — der Inhalt ist
derselbe:

1. **Review der eigenen Änderungen, zweimal.** Erst die Logik (tut es, was es soll?), dann
   die Form (Konventionen, Dokumentation, Tests). Befunde werden direkt behoben, nicht
   notiert. Ein zweiter Durchgang prüft gezielt das, was der erste geändert hat — er ist der
   Ort, an dem die meisten Fehler aus dem Abschluss selbst gefunden werden.
2. **Doku-Abgleich.** Was die Sitzung gelernt hat, steht an genau einem Ort: dauerhaft in
   der Fachdoku, offen in `docs/offen/`, projektübergreifend im `<admin-repo>`. Die
   Feedback-Datei ist spätestens jetzt fällig.
3. **Aufräumen** — nur das Eigene (Abschnitt 3, Wächter 2).
4. **Ausliefern über den dokumentierten Weg** des Projekts, nie über einen erfundenen.
   Ein Deploy fragt vorher den Steckbrief: Ist der Weg je gelaufen?
5. **Bericht**, der für sich allein steht: Was wurde gefunden, was getan, was bleibt
   offen — mit dem Weg, auf dem geprüft wurde. Zahlen ausgezählt. **Eine leere Ausgabe
   bestätigt nie**, sie widerspricht höchstens: Vor jedem „nichts gefunden" wird der
   Suchbefehl gegen einen bekannten Treffer bewiesen.

---

## 9. Was maschinell geprüft wird [Pflicht; Umfang nach Bedarf]

Ein Skript im `<admin-repo>` läuft über alle Repositories und meldet je Projekt
**Hinweise** (sollte) und **Alarme** (muss). Es ist Pflicht, weil Abschnitte 2, 4 und 6 sich
darauf verlassen; welche Prüfungen es enthält, wächst mit den Vorfällen. Es läuft als
**Wochenlauf** — ausgelöst vom Zeitplaner des Rechners (das gehört ins Rechner-Repository)
oder, wenn der Rechner nicht durchläuft, beim ersten Sitzungsstart der Woche; und es läuft
jederzeit von Hand für ein einzelnes Projekt. Bewährt haben sich:

| Prüfung | Warum |
|---|---|
| `.gitattributes` mit `* text=auto`; CRLF im Index nur dort, wo kein `-text`-Attribut es erlaubt | Zeilenenden driften beim ersten Kontakt mit einem anderen Betriebssystem; bewusste Ausnahmen (Referenzdateien, die byte-exakt bleiben müssen) dürfen nicht dauerhaft gemeldet werden |
| `.gitignore` deckt `.env` ab — **bevor** eine angelegt wird | Nachträglich ist das Geheimnis in der Historie |
| Remote vorhanden, nichts ungepusht, Arbeitsbaum sauber | Was nur auf einem Rechner liegt, ist keine Sicherung |
| Doku-Baum vollständig, Einträge mit ID und Schreiber-Tag | Abschnitt 5 |
| **Dieselbe ID zweimal in einer Datei** | Abschnitt 6; die Prüfung liest beide Eintragsformen und lässt Bereiche wie `A<n>–A<m>` in Ruhe |
| Gefüllte Rückmeldeschlitze | Wartende Arbeit — die teuerste Sorte, weil ein Mensch dafür gelesen hat |
| Nur eine Regeldatei, keine fremde Agentendatei — ein Symlink auf die Regeldatei ist erlaubt | Abschnitt 2 |
| Regeldatei unter der dokumentierten Größengrenze des Werkzeugs | Manche Werkzeuge kürzen oder ignorieren zu große Anweisungsdateien **still**. Ist keine Grenze dokumentiert: eine eigene setzen und prüfen, ob eine frische Sitzung den letzten Absatz der Datei wiedergeben kann |
| Steckbrief vorhanden und ohne Drift gegen die Messung | Abschnitt 4 |
| Host-Ports je Compose-Datei, Kollisionen über Projekte | Abschnitt 7 |

Drei Lehren aus dem Betrieb solcher Prüfungen:

- **Ein falsch-positiver Wächter ist schlimmer als keiner.** Eine Prüfung, die einen
  korrekten Eintrag meldet, wird weggeklickt — und meldet dann auch den echten Fall
  vergeblich. Jede Prüfung wird gegen den Bestand gemessen, bevor sie scharf geht: erst
  die Zahl der Treffer, dann die Frage, wie viele davon echt sind.
- **Jede Prüfung bekommt eine Positivkontrolle**: einen Stand, in dem sie anschlagen
  muss (eine alte Fassung aus der Historie, ein eingeschleuster Testfall). Eine Prüfung,
  die nie angeschlagen hat, hat nicht bewiesen, dass sie funktioniert.
- **Eine Prüfung, die ausfällt, meldet das laut.** Ein übersprungener Check sieht aus wie
  ein bestandener. Fehlt die Konfiguration, die er braucht, ist das ein Hinweis, kein
  stilles „ok".

Dazu passt ein zweiter Zähler, der den **Bestand** des Rückkanals je Projekt ausgibt (wie
viele offene Aufträge je Prioritätsmarke, wie viele Fragen in welchem Zustand) — aus den
Dateien gezählt, nicht als Tabelle gepflegt. Eine handgepflegte Übersicht ist eine Kopie
der Zahlen aus Dutzenden Dateien und widerspricht ihnen die meiste Zeit. Der Zähler meldet
Marken und Zeilenformen, die er nicht kennt, mit Datei und Zeile, statt sie zu
überspringen.

---

## 10. Reihenfolge für den Aufbau (Checkliste)

1. `<admin-repo>` anlegen (privat): `global/`, `docs/`, `feedback/`, `register/`,
   `scripts/`, eine Regeldatei, die sagt, was hierher gehört und was nicht (Abschnitt 1).
2. Kanon `global/regeln.md` schreiben — zunächst nur die Regeln, die aus einem echten
   Vorfall stammen. Sync-Skript mit Prüfsummen und den drei Zuständen (Abschnitt 2).
   Ausrollen in alle Werkzeug-Homes.
3. Je Werkzeug klären: Liest es im Projekt die **eine** Regeldatei (Einstellung, Symlink
   oder erzeugte Kopie)? Hat es Hooks, und wie werden sie registriert? Darf es im
   `<admin-repo>` schreiben? (Abschnitte 2, 3, 6)
4. Die drei Wächter bauen, mit `--test` in beide Richtungen prüfen, in jedes Home
   ausrollen und registrieren (Abschnitt 3). Wo ein Werkzeug keine Hooks hat: das Risiko
   im Kanon benennen.
5. Steckbrief-Generator schreiben; mit Projektfilter in jedes Projekt schreiben; den
   Satz „Lies den Steckbrief, bevor du eine Annahme bildest" in den Kanon (Abschnitt 4).
6. In jedem Projekt `docs/index.md` und `docs/offen/` anlegen; die nummerierten Bereiche
   nur dort, wo Inhalt umzieht. Vorhandene Listen umziehen, IDs vergeben, Schlitze
   ergänzen (Abschnitt 5).
7. Je Projekt eine Feedback-Datei anlegen, erste Befunde aus der Bestandsaufnahme
   eintragen; „Schritt 1 jeder Sitzung" in den Kanon (Abschnitt 6).
8. Abschluss-Fertigkeit schreiben und ausrollen — oder als Abschnitt in den Kanon
   (Abschnitt 8).
9. Konformitäts-Check schreiben, gegen den Bestand messen, Positivkontrollen festhalten,
   den Wochenlauf einrichten (Abschnitt 9).
10. Nach dem ersten Monat: Jede Regel, die zweimal gebrochen wurde, bekommt einen
    Mechanismus oder wird gestrichen.

---

## 11. Regeldatei-Baustein für den Kanon

Dieser Block kann als Anfang von `global/regeln.md` dienen. Er ist bewusst knapp;
Begründungen stehen in `docs/` des `<admin-repo>`, und jede Regel verweist dorthin — sonst
ist der Kanon der Ort, an dem Regeln ohne Grund stehen und deshalb gestrichen werden.

```markdown
# Regeln für jede KI-Sitzung in <projekte>/

## Schritt 1 jeder Sitzung: <admin-repo>/feedback/<projekt>.md
Lesen und abarbeiten, BEVOR die Aufgabe beginnt. Zuerst gefüllte Schlitze suchen (vom
Projektwurzelverzeichnis aus):
    grep -rnE --exclude=README.md '^ *- (💬 \*\*User:\*\*|🤖 \*\*[^*]+:\*\*)' \
         docs/offen/ <admin-repo>/feedback/ \
      | grep -vE '^[^:]+:[0-9]+: *- (💬|🤖) \*\*[^*]+:\*\* *—? *$'
Kleines sofort umsetzen, Fachliches fragen, Erledigtes als ✅ abhaken (Datum + Commit),
Falsches widersprechen. Was du dort schreibst, committest und pushst du selbst
(pull --rebase, dann push). Warum: docs/<rueckkanal>.md

## Der Steckbrief in der Regeldatei ist die Wahrheit - nicht dein Gedächtnis
Lies ihn, bevor du eine Annahme bildest. Ändere ihn nie von Hand; stimmt etwas nicht,
ist die Messung oder die zentrale Tabelle falsch (scripts/steckbrief). Ein `—` heißt
„nicht messbar". Warum: docs/<steckbrief>.md

## Offener Bestand: docs/offen/ - eine Datei je Art, jeder Eintrag mit ID und Tag
fehler · aufgaben · ideen · fragen · erledigt. Keine neue Liste, kein Datum im Namen,
keine Statusnotiz in der Regeldatei. Erledigtes zieht vollständig um. Warum: docs/<doku>.md

## Genau eine Regeldatei je Projekt. Befunde ins Repo, nicht in den Agentenspeicher.

## Löschen: eigener Müll ja, fremde Daten nur nach Rücksprache
Jede Variable in einem löschenden Pfad mit `:?`, gesetzt im selben Aufruf - und `:?`
fängt nur die leere Variable, nicht die falsche. Warum: docs/<waechter>.md

## Parallele Sitzungen
Wenn möglich eigener Arbeitsbaum. Nie `git add -A` / `.` / <verzeichnis>. Prozesse über
die PID. Fremde Änderungen liegen lassen und im Bericht nennen. Vor „läuft" ein Durchlauf
durch die echte Oberfläche.

## Compose-Ports an 127.0.0.1 binden; Ausnahmen bewusst und je Zeile.

*Kanon ist <admin-repo>/global/regeln.md. Die Dateien in den Werkzeug-Homes sind
Ausrollziele - was dort direkt geändert wird, ist beim nächsten Abgleich wieder weg.*
```

---

## Glossar

| Begriff | Bedeutung hier |
|---|---|
| **Kanon** | die eine geschriebene Fassung der Regeln im `<admin-repo>`; alles andere ist davon erzeugt |
| **Ausrollziel** | die Datei im Home eines Werkzeugs, die aus dem Kanon erzeugt wird |
| **Tür** | eine werkzeugspezifische Anweisungsdatei; sie führt in die Dokumentation, sie ist keine |
| **Fertigkeit** | ein wiederverwendbarer Ablauf, den der Mensch per Befehl im Werkzeug auslöst (je nach Produkt „Skill" oder „Slash-Befehl") |
| **Hook / Wächter** | ein Programm, das vor einem Werkzeugaufruf läuft und ihn ablehnen kann |
| **Steckbrief** | der erzeugte Block mit gemessenen und zentral festgehaltenen Fakten in der Regeldatei jedes Projekts |
| **Rückkanal** | `<admin-repo>/feedback/<projekt>.md` — die zentrale Sicht auf ein Projekt, als Zeilen für genau dieses Projekt |
| **Schlitz** | eine der zwei Rückmeldezeilen je Eintrag (`💬 User`, `🤖 <Tag>`) |
| **Schreiber-Tag** | `@<werkzeug>` oder `@mensch` hinter der ID: wer den Eintrag geschrieben hat |
| **Prioritätsmarke** | das Zeichen zwischen Checkbox und ID (🔴 🟡 ⚪ ⬜); eine Skala, die der Zähler kennt |
| **Grabstein** | ein erledigter Eintrag, der in der Arbeitsliste von `docs/offen/` stehen bleibt — verboten; im Rückkanal dagegen bleibt `✅` stehen |
| **Positivkontrolle** | ein Stand, in dem eine Prüfung anschlagen **muss**; ohne sie ist eine stumme Prüfung unbewiesen |
| **Wochenlauf** | der regelmäßige Lauf des Konformitäts-Checks und des filterlosen Steckbrief-Generators über alle Repositories |
| **Worktree** | ein zweiter Arbeitsbaum desselben Repositories in einem eigenen Verzeichnis (`git worktree`); dort ist `.git` eine Datei, kein Ordner |
| **Heredoc** | mehrzeiliger Text in einem Shell-Befehl (`cat <<'EOF' … EOF`); sein Inhalt ist Daten, kein Befehl — Wächter müssen das unterscheiden |
| **Drift / Konflikt** | ein Ziel weicht vom Kanon ab / mehrere Ziele weichen vom Kanon und voneinander ab |
