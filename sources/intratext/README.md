# IntraText HTML Source

Dieser Ordner enthalt den gezielten HTML-Download der IntraText-Ausgabe von:

Alfonso Maria de Liguori, *Le Glorie di Maria*  
https://www.intratext.com/ixt/ITASA0013/_index.htm

## Download

Der Download erfolgt mit:

```sh
python3 scripts/download_intratext.py --fetcher curl --delay 0.5
```

Das Script liest den Index, extrahiert die dort verlinkten Textseiten und laedt jeweils die IntraText-Variante mit ausgeblendeten Konkordanzlinks:

- normale Seite: `_P7.HTM`
- verwendete Seite: `__P7.HTM`

Die Rohdateien liegen in [raw_html](raw_html). Das Manifest mit URLs, Reihenfolge, Dateigroessen und SHA256-Pruefsummen liegt in [manifest.json](manifest.json).

## Lizenz

IntraText nennt fuer Inhalte der Digital Library, sofern nicht anders angegeben, die Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported License.

Die TEI-Konversion soll diese Quelle und Lizenz im `teiHeader` dokumentieren.
