# IntraText nach TEI: Wiederverwendbarer Workflow

Diese Dokumentation beschreibt das Vorgehen, mit dem die italienische IntraText-Fassung der *Glorie di Maria* heruntergeladen, lokal archiviert und in eine erste semantische TEI-Fassung ueberfuehrt wurde. Sie ist zugleich als Vorlage fuer andere Texte des heiligen Alphons von Liguori gedacht, besonders fuer weitere IntraText-Texte wie die *Massime eterne*.

## Ziel

Der Workflow trennt vier Ebenen:

- gezielter, reproduzierbarer Download der IntraText-HTML-Dateien;
- lokale Sicherung der Rohquellen mit Manifest und Pruefsummen;
- generische HTML-nach-TEI-Konversion;
- werkbezogene semantische Nachstrukturierung.

Fuer neue Projekte soll moeglichst viel aus diesem Repository wiederverwendet werden. Besonders wiederverwendbar sind der Downloader, der HTML-Parser, die Fussnotenlogik, die Behandlung von Seitenumbruechen und die Dokumentationsstruktur. Neu zu entwickeln ist meist die eigentliche semantische Gliederung des jeweiligen Werks.

## Vorlage im neuen Projekt

Wenn ein neues Projekt begonnen wird, sollte dort zu Beginn folgender Hinweis an Codex gegeben werden:

```text
Nutze /Users/jakubsimek/GitLab/Glorie_di_Maria als Vorlage.
Uebernimm insbesondere die IntraText-Download-Logik, die HTML-zu-TEI-Parserlogik, Manifeststruktur, Fussnotenbehandlung, pb-Behandlung und die Dokumentationsmuster.
```

Das neue Projekt sollte moeglichst dieselbe Grundstruktur erhalten:

```text
docs/
data/
sources/intratext/raw_html/
edition/it/tei/
scripts/
```

## Quellenpruefung

Vor dem Download wird die IntraText-Seite des Werks geprueft:

- Welche IntraText-ID hat der Text, z. B. `ITASA0013`?
- Wie lautet die Index-URL, z. B. `https://www.intratext.com/ixt/ITASA0013/_index.htm`?
- Welche Ausgabe nennt IntraText als Druckgrundlage?
- Gibt es abweichende Lizenz- oder Copyright-Hinweise?
- Ist der Text vollstaendig oder nur ein Auszug?

Fuer die *Glorie di Maria* wurde als Lizenzannahme dokumentiert: IntraText stellt Inhalte der Digital Library nach eigener Copyright-Seite grundsaetzlich unter Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported bereit, sofern nicht anders angegeben. Diese Annahme soll in jedem neuen Projekt erneut anhand der konkreten IntraText-Seite geprueft und dokumentiert werden.

## Download

Der aktuelle Downloader liegt in:

```text
scripts/download_intratext.py
```

Er arbeitet so:

- laedt die `_index.htm`-Datei;
- extrahiert daraus nur die verlinkten Textseiten im Muster `_P*.HTM`;
- wandelt diese URLs in die konkordanzfreien Varianten `__P*.HTM` um;
- speichert die Rohdateien unter `sources/intratext/raw_html/`;
- erzeugt `sources/intratext/manifest.json` mit Reihenfolge, Titel, URL, Dateigroesse und SHA256-Pruefsumme.

Die konkordanzfreie Variante ist wichtig: IntraText bietet auf den Seiten die Moeglichkeit, Konkordanzlinks auszublenden. Technisch wird aus `_P7.HTM` die Seite `__P7.HTM`. Dadurch enthaelt das HTML deutlich weniger stoerende Wortlinks.

Ausfuehrung in diesem Projekt:

```sh
python3 scripts/download_intratext.py --fetcher curl --delay 0.5
```

`--fetcher curl` wurde verwendet, weil `curl` in dieser Umgebung stabiler mit Netzwerk und Zertifikaten funktionierte als `urllib`.

## Anpassungen fuer ein neues Werk

Im Downloader muessen fuer ein neues Werk mindestens diese Werte angepasst werden:

```python
BASE_URL = "https://www.intratext.com/ixt/ITASA0013/"
INDEX_URL = urljoin(BASE_URL, "_index.htm")
OUT_DIR = Path("sources/intratext")
USER_AGENT = "Glorie-di-Maria-TEI/0.1 (+noncommercial scholarly edition)"
```

Ebenso muss im Manifest die `work`-Sektion angepasst werden:

```python
"title": "Le Glorie di Maria",
"author": "S. Alfonso Maria de Liguori",
"intratext_id": "ITASA0013",
"index_url": INDEX_URL,
"source_note": "...",
"license": "...",
"license_url": "...",
```

Sinnvoll waere kuenftig eine Generalisierung ueber Kommandozeilenoptionen, z. B.:

```sh
python3 scripts/download_intratext.py \
  --base-url https://www.intratext.com/ixt/ITASAxxxx/ \
  --title "Massime eterne" \
  --author "Alfonso Maria de Liguori" \
  --out sources/intratext \
  --fetcher curl \
  --delay 0.5
```

In diesem Repository ist der Downloader noch werkbezogen, aber seine Logik ist einfach auf andere IntraText-Werke uebertragbar.

## Manifest

Das Manifest ist die Bruecke zwischen Download und TEI-Konversion. Es dokumentiert:

- Werkmetadaten;
- Indexseite;
- Reihenfolge der heruntergeladenen Seiten;
- lokale Dateipfade;
- Original-URLs;
- Dateigroessen;
- SHA256-Pruefsummen.

Diese Datei sollte nie manuell ausgeduennt werden. Sie ist wichtig fuer Reproduzierbarkeit und spaetere Quellenkontrolle.

## Generische HTML-zu-TEI-Konversion

Der aktuelle Konverter liegt in:

```text
scripts/convert_intratext_to_tei.py
```

Die unteren Parser-Funktionen sind weitgehend generisch und koennen fuer andere IntraText-Texte wiederverwendet werden:

- `content_fragment`
- `IntraTextContentParser`
- `parse_page`
- `clean_inline`
- `merge_page_split_paragraphs`
- `milestone_for`
- `build_back`

Diese Logik leistet:

- Extraktion des eigentlichen IntraText-Inhalts zwischen Kopf und Fussbereich;
- Erkennung von HTML-Absaetzen als `<p>`;
- Erhalt von Kursiv/Fett als `<hi rend="italic">` und `<hi rend="bold">`;
- Erkennung von Fussnotenverweisen als `<ref type="note" target="#note-...">`;
- Erkennung der Fussnotentexte als `<note xml:id="note-..." n="...">`;
- Erkennung gedruckter Seitenmarker als `<pb n="..."/>`;
- Erzeugung von IntraText-Seitenmarkern als `<milestone unit="intratext-page">`;
- Zusammenfuehrung kuenstlich getrennter Absaetze ueber Seitenumbrueche hinweg.

## Absatz- und Seitenumbruchlogik

IntraText setzt an Seitenwechseln manchmal einen neuen HTML-Absatz, obwohl im Druck kein neuer Absatz beginnt. Der Konverter behandelt das konservativ:

```xml
<p>erster Teil</p>
<pb n="..."/>
<p>zweiter Teil</p>
```

wird zu:

```xml
<p>erster Teil <pb n="..."/> zweiter Teil</p>
```

aber nur wenn die Grenze syntaktisch nach Fortsetzung aussieht. Kriterien:

- der erste Teil endet nicht mit Satzschlusszeichen;
- oder der zweite Teil beginnt klein bzw. mit Fortsetzungszeichen wie Komma, Punkt, Semikolon, Klammer.

Das `<pb>` bleibt erhalten, wird aber in den Absatz integriert. So bleibt die Druckseitenreferenz erhalten, ohne die Absatzstruktur zu verfaelschen.

## Fussnoten

IntraText-Fussnoten werden im HTML typischerweise ueber hochgestellte Links und Anker im Notenbereich modelliert. Der Parser:

- liest das sichtbare hochgestellte Label;
- normalisiert das Ziel zu einem XML-tauglichen Fragment;
- erzeugt einen `<ref>` im Text;
- sammelt den Notentext im Rueckteil.

Ergebnis:

```xml
<ref type="note" target="#note-B">1</ref>
```

und im Rueckteil:

```xml
<note xml:id="note-B" n="B">...</note>
```

Nach der Konversion sollte geprueft werden:

- Sind alle `target`-Werte vorhanden?
- Gibt es doppelte `xml:id`-Werte?
- Gibt es unreferenzierte Noten?

## Werkbezogene semantische Struktur

Der wichtigste nicht-generische Teil ist die semantische Gliederung. In `convert_intratext_to_tei.py` ist dieser Teil stark auf die *Glorie di Maria* zugeschnitten:

- `build_front_divs`
- `build_part_one`
- `build_part_two`
- `build_discorsi`
- `build_examples_page`
- `build_prayers_page`
- werkbezogene Regex-Muster fuer `§`, `DISCORSO`, `Punto`, `Esempio`, `Preghiera`, `OSSEQUIO` usw.

Fuer ein neues Werk sollte man zuerst eine einfache, konservative TEI-Fassung erzeugen:

```xml
<body>
  <div type="intratext-page" xml:id="src-p1">...</div>
  <div type="intratext-page" xml:id="src-p2">...</div>
</body>
```

Danach wird anhand des konkreten Textes entschieden:

- Welche Seiten gehoeren zum Frontmatter?
- Gibt es Teile, Kapitel, Betrachtungen, Punkte, Gebete, Beispiele?
- Welche Ueberschriftenmuster sind verlaesslich?
- Welche Strukturen bleiben besser als Absatz statt spekulativ ausgezeichnet?

Erst danach sollte die semantische TEI-Struktur gebaut werden.

## TEI-Header

Der TEI-Header soll mindestens enthalten:

- Titel und Autor;
- Verantwortung der digitalen Quelle;
- Lizenzhinweis;
- IntraText-URL;
- Druckquelle, sofern IntraText sie nennt;
- Hinweis auf die konkordanzfreie `__P*.HTM`-Variante;
- Erzeugungsdatum bzw. Download-Datum aus dem Manifest.

Fuer neue Werke muss der Header nicht blind kopiert werden. Er sollte aus dem Manifest und aus der konkreten Quellenlage des Werks erzeugt werden.

## Validierung

Nach jedem Download:

```sh
python3 scripts/download_intratext.py --fetcher curl --delay 0.5
```

pruefen:

```sh
python3 -m json.tool sources/intratext/manifest.json >/dev/null
```

Nach jeder TEI-Konversion:

```sh
python3 scripts/convert_intratext_to_tei.py
python3 -m xml.etree.ElementTree edition/it/tei/glorie-di-maria.xml
```

Zusaetzlich sinnvoll:

```sh
rg '<ref type="note"' edition/it/tei/glorie-di-maria.xml
rg '<note xml:id=' edition/it/tei/glorie-di-maria.xml
rg '<pb ' edition/it/tei/glorie-di-maria.xml
```

Bei einem neuen Werk sollte Codex ausserdem ein kleines Pruefskript oder eine Auswertung erstellen fuer:

- Anzahl der Textseiten;
- Anzahl der `<pb>`-Marker;
- Anzahl der Fussnoten und Fussnotenverweise;
- fehlende Fussnotenziele;
- doppelte `xml:id`-Werte;
- auffaellige leere oder sehr kurze Abschnitte.

## Dokumentation im neuen Projekt

Jedes neue Projekt sollte mindestens diese Dateien erhalten:

```text
README.md
docs/editorial-guidelines.md
sources/source-plan.md
sources/intratext/README.md
edition/it/tei/README.md
data/bibliography.yml
```

Der jeweilige `sources/intratext/README.md` sollte nennen:

- IntraText-Index-URL;
- Download-Befehl;
- Hinweis auf `__P*.HTM`;
- Manifest-Pfad;
- Lizenzannahme;
- Datum oder Stand des Downloads.

Der jeweilige `edition/it/tei/README.md` sollte nennen:

- Konversionsbefehl;
- Eingabe- und Ausgabedateien;
- aktuelles TEI-Mapping;
- bekannte Grenzen;
- offene editorische Entscheidungen.

## Typische Stolperstellen

- IntraText-Dateien sind haeufig `iso-8859-1`, nicht UTF-8.
- Textseiten koennen alphanumerisch benannt sein, z. B. `_PA.HTM`, nicht nur `_P1.HTM`.
- Die konkordanzfreie Variante ist durch doppelten Unterstrich erreichbar, z. B. `__PA.HTM`.
- IntraText-Seiten sind nicht identisch mit Druckseiten; Druckseiten erscheinen als eigene Marker im Text.
- Gedruckte Seitenzahlen koennen in mehrbaendigen Ausgaben ohne Bandangabe erscheinen.
- Fussnoten-IDs koennen alphanumerisch sein.
- Ueberschriften sind nicht immer semantisch eindeutig; lieber konservativ auszeichnen.
- HTML-Absatzgrenzen an Seitenumbruechen duerfen nicht unkritisch als echte Absatzgrenzen uebernommen werden.

## Empfohlener Ablauf fuer Massime eterne

1. Neues Repository anlegen.
2. Grundstruktur wie oben erstellen.
3. IntraText-Index-URL der *Massime eterne* eintragen.
4. Downloader aus diesem Repository kopieren und Metadaten anpassen.
5. Download ausfuehren und Manifest pruefen.
6. Zuerst generische TEI nach IntraText-Seiten erzeugen.
7. Roh-TEI und HTML stichprobenartig vergleichen.
8. Ueberschriftenmuster analysieren.
9. Semantische Struktur definieren.
10. Konverter werkbezogen erweitern.
11. TEI validieren und Counts pruefen.
12. Quellen-, Lizenz- und Konversionsentscheidungen dokumentieren.

## Kurzfassung fuer Codex

In einem neuen Projekt kann diese Arbeitsanweisung verwendet werden:

```text
Erzeuge fuer diesen IntraText-Text eine TEI-Edition nach dem Muster von
/Users/jakubsimek/GitLab/Glorie_di_Maria.

Bitte:
- kopiere bzw. adaptiere zuerst die Download-Logik aus scripts/download_intratext.py;
- nutze die konkordanzfreien __P*.HTM-Seiten;
- erstelle ein Manifest mit URL, Reihenfolge, Titel, Dateigroesse und SHA256;
- uebernimm die generische Parserlogik aus scripts/convert_intratext_to_tei.py;
- erzeuge zuerst eine konservative TEI nach IntraText-Seiten;
- analysiere danach die Werkstruktur und schlage semantische TEI-divs vor;
- bewahre pb, Fussnoten, hi-renditions und IntraText-Seitenmilestones;
- dokumentiere alle Quellen-, Lizenz- und Konversionsentscheidungen.
```
