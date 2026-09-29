# ai-playbooks

Anleitungen, die man **einer KI gibt**, damit sie gemeinsam mit einem Menschen etwas
aufbaut: Server absichern, Betrieb organisieren, wiederkehrende Aufgaben sauber
erledigen.

Jede Anleitung ist ein eigenes Kapitel und **funktioniert für sich allein**. Du musst
nicht das ganze Repo kennen. Ein Link auf das jeweilige Kapitel genügt.

## So benutzt du ein Kapitel

1. Such dir unten das passende Kapitel aus.
2. Öffne es und klick auf **„Raw“**. Das ist die reine Textdatei.
3. Gib deiner KI (Claude, ChatGPT, Codex, …) diesen Link oder den Inhalt, zum Beispiel so:

   > Lies diese Anleitung vollständig: `<Raw-Link>`
   > Bau das mit mir für meine Umgebung auf. Frag mich zuerst nach meiner
   > Infrastruktur, und erklär mir jeden Schritt, den ich selbst machen muss.

Die KI stellt dir dann Fragen, erklärt die Schritte, die du selbst machen musst (z. B.
Zugänge und Tokens anlegen), und übernimmt den Rest.

## Kapitel

| Kapitel | Wofür |
|---|---|
| [Server-Betrieb](server-betrieb/README.md) | Eigene Server absichern und dauerhaft betreiben: Bestandsaufnahme und Schutzbedarf, Kontoschutz, getestete Backups und Rückwege, SSH- und Container-Härtung, externe und lokale Überwachung mit Push-Alarmen, Audits, Update-Prozess, Einbruchs-Notfall; optional SSH-Gate, Sperren und CDN-Honeypots |

*Weitere Kapitel folgen.*

## Gemeinsame Grundsätze

Diese Regeln gelten für alle Kapitel. Jedes Kapitel wiederholt die wichtigsten davon
selbst, damit es allein funktioniert.

- **Keine Geheimnisse im Chat oder im Repo.** Passwörter, Tokens und private Schlüssel
  legt der Mensch selbst an. Die KI kennt nur Variablennamen.
- **Die KI erklärt, der Mensch entscheidet.** Alles mit Zugangsdaten, Konten oder
  unumkehrbaren Folgen macht der Mensch nach Anleitung.
- **Befund vor Empfehlung.** Erst messen, dann folgern, mit Zahl, Quelle und Datum.
- **Zu jeder Sperre ein Rückweg,** einmal wirklich ausprobiert.
- **Nichts blind übernehmen.** Die Kapitel beschreiben Muster und Begründungen, keine
  fertigen Werte für fremde Umgebungen.

## Pflege

Gepflegt von **dbtr-digital**. Wer hier veröffentlichen darf und was vor jedem
Veröffentlichen geprüft wird, steht in [`CLAUDE.md`](CLAUDE.md).

## Mitmachen

Fehler gefunden oder eine Verbesserung? Gern als Issue oder Pull Request.

## Lizenz

- **Texte und Anleitungen:** [CC BY 4.0](LICENSE). Frei nutzbar und veränderbar, auch
  kommerziell, bei Nennung der Quelle, wenn du das Material weitergibst.
- **Skripte** (`scripts/`, `.github/`): [MIT](LICENSE-CODE).

Rechteinhaber und Vorschlag für die Namensnennung: [`NOTICE`](NOTICE). Wer eine Anleitung
nur seiner KI gibt, um damit eigene Systeme aufzubauen, muss nichts nennen.
