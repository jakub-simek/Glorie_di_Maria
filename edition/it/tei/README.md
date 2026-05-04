# TEI Conversion

Dieser Ordner enthaelt die erste automatische TEI-Konversion des italienischen IntraText-Downloads.

## Erzeugung

```sh
python3 scripts/convert_intratext_to_tei.py
```

Eingabe:

- [../../../sources/intratext/manifest.json](../../../sources/intratext/manifest.json)
- [../../../sources/intratext/raw_html](../../../sources/intratext/raw_html)

Ausgabe:

- [glorie-di-maria.xml](glorie-di-maria.xml)

## Aktuelles Mapping

- Werkvorspann und editorische Einleitungen: `<front>`
- Werkhauptteil: `<body>`
- Notenapparat: `<back><div type="notes">`
- Werkteile: `<div type="part">`
- Kapitel: `<div type="chapter">`
- Paragraphen, Discorsi, Dolori, Virtues, Ossequi und einzelne Beispiele/Orazioni: semantische `<div>`-Elemente mit passenden `type`-Werten
- IntraText-Seite: `<milestone unit="intratext-page">`
- Seitennummern der Druckquelle: `<pb n="..."/>`
- HTML-Absatz: `<p>`
- Kursiv/Fett: `<hi rend="italic">`, `<hi rend="bold">`
- Fussnotenverweis: `<ref type="note" target="#note-...">`
- Fussnotentext: `<note xml:id="note-..." n="...">`

## Bekannte Grenzen

Die Konversion ist ein erster semantischer, wohlgeformter TEI-Stand. Sie erkennt die Hauptgliederung des Werks automatisch, bleibt aber konservativ: unsichere Unterstrukturen werden als Absätze belassen statt spekulativ ausgezeichnet.

IntraText setzt Absatze an Seitenwechseln teilweise neu an. Der Konverter fuehrt solche geteilten Absatze konservativ wieder zusammen, wenn die Grenze syntaktisch nach Fortsetzung aussieht, zum Beispiel wenn der erste Teil ohne Satzschluss endet oder der zweite Teil klein weiterlaeuft. Das `<pb>` bleibt dann innerhalb des Absatzes erhalten.
