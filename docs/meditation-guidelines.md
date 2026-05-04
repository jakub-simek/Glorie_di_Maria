# Richtlinien fuer Meditationen

Diese Richtlinien beschreiben, wie Meditationstexte zur digitalen Edition der *Glorie di Maria* erstellt werden sollen.

## Ziel

Die Meditationen sollen keine Paraphrase des italienischen Textes und kein wissenschaftlicher Kommentar sein. Sie sind geistliche Begleittexte, die aus einem konkreten Abschnitt der Edition hervorgehen und diesen fuer Gebet, Betrachtung und innere Aneignung erschliessen.

Jede Meditation soll textnah bleiben, aber eine eigene kontemplative Stimme haben.

## Sprache

Die lateinischen Meditationen werden in kirchlich gepraegtem Latein verfasst.

Angestrebt ist:

- klare, gut lesbare Perioden;
- biblischer und liturgischer Ton;
- keine klassizistische Kuenstlichkeit;
- keine modernen technischen Begriffe, sofern sie nicht noetig sind;
- sparsame, aber bewusste Verwendung traditioneller Formeln.

Die Sprache darf schlicht sein. Sie soll eher wie geistliche Lesung klingen als wie akademische Prosa.

Das neu verfasste Latein der Meditationen muss immer auf sprachliche Richtigkeit geprueft werden: Grammatik, Kasus, Kongruenz, Tempusgebrauch, Syntax und idiomatische Angemessenheit. Diese Pruefung betrifft nicht die Form von Zitaten; Zitate werden nach der kontrollierten Quelle wiedergegeben, auch wenn Orthographie oder Wortlaut vom neu verfassten Stil abweichen.

## Rhetorische Haltung

Die Meditation richtet sich nicht an einen imaginaeren Leser, sondern an die eigene Seele.

Bevorzugt sind Formen der Selbstanrede, z. B. `anima mea`, `cor meum`, `recordare`, `vide`, `audi`, `dilata`. Der Text darf aus dem `ego` sprechen, soll aber keine Predigt an andere und keine belehrende Leseransprache werden.

## Theologischer Rahmen

Die Meditationen sollen entschieden christozentrisch und kirchlich sein.

Grundsaetze:

- Die Theologie der Meditationen muss traditionell katholisch sein.
- Modernistische Tendenzen, relativierende Umdeutungen des Glaubens und blosse Symbolisierungen dogmatischer Aussagen sind zu meiden.
- Maria wird nie als Ziel an Stelle Christi dargestellt.
- Marianische Verehrung fuehrt zu Christus und zur Anbetung Gottes.
- Christus bleibt der eine Erloeser und Mittler der Gerechtigkeit.
- Die Fuersprache Mariens und der Heiligen wird im Rahmen der communio sanctorum verstanden.
- Aussagen ueber Maria sollen mit der Lehre der Kirche und der gesunden Theologie vereinbar bleiben.

Wo eine marianische Formulierung stark ist, soll der innere Bezug zu Christus, Gnade, Kirche oder Heil deutlich bleiben.

## Quellenklang

Jede Meditation soll, soweit passend, Resonanzen aus mehreren Traditionsschichten aufnehmen:

- Heilige Schrift;
- Liturgie und Gebetssprache der Kirche;
- Kirchenvaeter;
- mittelalterliche Theologie und Spiritualitaet;
- Catechismus Romanus.

Diese Quellen muessen nicht als gelehrter Apparat im Haupttext erscheinen. Sie sollen den Text tragen und faerben. Am Ende kann ein kurzer Abschnitt `Fontes Resonantes` die wichtigsten Anspielungen nennen.

## Umgang mit Zitaten

Kurze lateinische Formeln duerfen direkt verwendet werden, besonders wenn sie biblisch, liturgisch oder traditionell fest gepraegt sind.

Alle direkten Zitate muessen als Zitate erkennbar sein. In Markdown werden sie grundsaetzlich kursiv gesetzt und unmittelbar danach mit einer Quellenangabe versehen:

`*Magnificat anima mea Dominum* (Lc 1, 46).`

Alle Zitate muessen vor der Verwendung genau kontrolliert und anhand einer verlaesslichen Ausgabe oder Quelle ueberprueft werden. Sie muessen echt sein. Kein Zitat darf erfunden, aus dem Gedaechtnis frei rekonstruiert oder einer Autoritaet nur ungefaehr zugeschrieben werden.

Das gilt fuer:

- biblische Zitate;
- liturgische Zitate;
- patristische Zitate;
- mittelalterliche Quellen;
- Catechismus Romanus und andere lehramtliche oder katechetische Quellen;
- Zitate aus der italienischen Vorlage.

Die Quellenangabe steht direkt hinter dem Zitat, nicht nur gesammelt am Ende. Sie soll so genau wie praktikabel sein:

- Bibel: Buch, Kapitel, Vers, z. B. `(Lc 1, 46)`;
- Patristik und Mittelalter: Autor, Werk, wenn moeglich Buch/Homilie/Kapitel/Abschnitt;
- Catechismus Romanus: Teil und Kapitel/Abschnitt nach der verwendeten Ausgabe, soweit bekannt;
- Editionstext: TEI-`xml:id`, Seite oder Abschnitt.

Fuer biblische Zitate wird nicht die Nova Vulgata verwendet. Massgeblich ist die traditionelle Vulgata, nach Moeglichkeit die Clementina. Wenn sich die Vulgata-Fassungen unterscheiden, ist die verwendete Fassung zu notieren.

Typographisch steht in Bibelstellenangaben hinter dem Komma nach der Kapitelnummer immer ein Leerzeichen: `(Lc 1, 46)`, nicht `(Lc 1,46)`.

In von-bis-Angaben wird immer der Halbgeviertstrich U+2013 verwendet, nicht der einfache Bindestrich: `(Io 19, 26–27)`, nicht `(Io 19, 26-27)`.

Laengere Quellenpassagen sollen nicht einfach abgeschrieben werden. Besser ist:

- anspielen;
- verdichten;
- in eigener Meditation fortfuehren;
- die Quelle am Ende knapp nennen, wenn es sich nur um eine Reminiszenz handelt.

Der Abschnitt `Fontes Resonantes` bleibt sinnvoll, aber er ersetzt die direkte Quellenangabe bei Zitaten nicht. Dort werden vor allem nichtwoertliche Anspielungen, Motive und Traditionslinien gesammelt.

## Aufbau Einer Meditation

Empfohlene Grundstruktur:

- `Relatio`: Bezug zur Edition, Abschnitt, Thema, Status.
- `Textus Fundamentalis`: kurzer Ausgangspunkt aus dem italienischen Text oder eine knappe Paraphrase.
- `Meditatio`: eigentlicher Betrachtungstext.
- `Oratio`: kurzes Gebet am Ende.
- `Fontes Resonantes`: knappe Liste wichtiger biblischer und theologischer Resonanzen.

Diese Struktur kann angepasst werden, wenn der Abschnitt es verlangt. Die Meditation selbst soll aber nicht durch Apparate erdrueckt werden.

## Bezug Zur Edition

Jede Meditation muss eindeutig auf einen Abschnitt der TEI verweisen.

Moegliche Angaben:

- `xml:id` des TEI-Abschnitts;
- Anfangsworte;
- Seitenmarker, falls hilfreich;
- Kapitel, Paragraph oder Unterabschnitt.

Die Meditationen bleiben ausserhalb der TEI-Datei, solange ihr Modell noch erprobt wird.

## Stil

Die Meditation soll:

- aus dem betrachteten Abschnitt wirklich hervorgehen;
- die eigene Seele direkt oder indirekt ins Gebet fuehren;
- geistliche Waerme haben, ohne sentimental zu werden;
- lehrhaft sein, ohne wie ein Traktat zu klingen;
- konkrete innere Bewegungen ansprechen: Glaube, Hoffnung, Liebe, Demut, Vertrauen, Umkehr.

Zu vermeiden:

- blosse Inhaltszusammenfassung;
- polemischer Ton;
- ungesicherte dogmatische Uebersteigerung;
- ueberladene Quellenkataloge im Haupttext;
- zu moderne oder psychologisierende Sprache.

## Dateinamen

Lateinische Meditationen liegen vorerst unter:

`meditations/la/`

Empfohlenes Schema:

`001-kurzer-titel.md`

Die Nummer folgt der Arbeitsreihenfolge, nicht zwingend der endgueltigen Editionsnummerierung.
