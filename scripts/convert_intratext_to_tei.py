#!/usr/bin/env python3
"""Convert downloaded IntraText HTML pages to a first-pass TEI document."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from html import escape
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from xml.etree import ElementTree


MANIFEST = Path("sources/intratext/manifest.json")
OUT_FILE = Path("edition/it/tei/glorie-di-maria.xml")
TEI_NS = "http://www.tei-c.org/ns/1.0"


@dataclass
class ParsedPage:
    blocks: list[str]
    notes: list[str]


def attrs_dict(attrs: list[tuple[str, str | None]]) -> dict[str, str]:
    return {name.lower(): value or "" for name, value in attrs}


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text)


def xml_id_fragment(value: str) -> str:
    value = value.strip().lstrip("$-#")
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", value)


def wrap_hi(text: str, rend_stack: list[str]) -> str:
    escaped = escape(normalize_text(text), quote=False)
    if not escaped:
        return ""
    for rend in reversed(rend_stack):
        escaped = f'<hi rend="{rend}">{escaped}</hi>'
    return escaped


class IntraTextContentParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.blocks: list[str] = []
        self.notes: list[str] = []
        self.rend_stack: list[str] = []
        self.current_p: list[str] | None = None
        self.in_sup = False
        self.sup_label: list[str] = []
        self.sup_target: str | None = None
        self.in_notes = False
        self.current_note_id: str | None = None
        self.current_note: list[str] = []
        self.in_note_anchor = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        attr = attrs_dict(attrs)

        if tag == "hr" and attr.get("align", "").lower().startswith("left"):
            self.in_notes = True
            self._close_p()
            return

        if tag == "p" and not self.in_notes:
            self._close_p()
            self.current_p = []
            return

        if tag == "i":
            self.rend_stack.append("italic")
            return

        if tag == "b":
            self.rend_stack.append("bold")
            return

        if tag == "sup":
            self.in_sup = True
            self.sup_label = []
            self.sup_target = None
            return

        if tag == "a":
            name = attr.get("name", "")
            href = attr.get("href", "")
            if self.in_sup and href.startswith("#$"):
                self.sup_target = xml_id_fragment(href)
                return
            if self.in_notes and name.startswith("$"):
                self._close_note()
                self.current_note_id = xml_id_fragment(name)
                self.current_note = []
                self.in_note_anchor = True
                return

        if tag == "br":
            self._append_text(" ")

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag == "p":
            self._close_p()
            return
        if tag in {"i", "b"} and self.rend_stack:
            expected = "italic" if tag == "i" else "bold"
            if self.rend_stack[-1] == expected:
                self.rend_stack.pop()
            elif expected in self.rend_stack:
                self.rend_stack.remove(expected)
            return
        if tag == "sup":
            label = escape("".join(self.sup_label).strip(), quote=False)
            if label and self.sup_target:
                target = self.sup_target
                self._append_xml(f'<ref type="note" target="#note-{target}">{label}</ref>')
            elif label:
                self._append_xml(f'<hi rend="superscript">{label}</hi>')
            self.in_sup = False
            self.sup_label = []
            self.sup_target = None
            return
        if tag == "a" and self.in_note_anchor:
            self.in_note_anchor = False

    def handle_data(self, data: str) -> None:
        page_match = re.fullmatch(r"\s*-\s*(\d+)\s*-\s*", data)
        if page_match and not self.in_notes:
            self._close_p()
            self.blocks.append(f'<pb n="{page_match.group(1)}"/>')
            return

        if self.in_sup:
            self.sup_label.append(data)
            return

        if self.in_note_anchor:
            return

        self._append_text(data)

    def close(self) -> None:
        super().close()
        self._close_p()
        self._close_note()

    def _append_text(self, data: str) -> None:
        if not data:
            return
        target = self.current_note if self.in_notes and self.current_note_id else self.current_p
        if target is None:
            return
        target.append(wrap_hi(data, self.rend_stack))

    def _append_xml(self, xml: str) -> None:
        target = self.current_note if self.in_notes and self.current_note_id else self.current_p
        if target is not None:
            target.append(xml)

    def _close_p(self) -> None:
        if self.current_p is None:
            return
        content = clean_inline("".join(self.current_p))
        if content:
            self.blocks.append(f"<p>{content}</p>")
        self.current_p = None

    def _close_note(self) -> None:
        if not self.current_note_id:
            return
        content = clean_inline("".join(self.current_note))
        if content:
            self.notes.append(f'<note xml:id="note-{self.current_note_id}" n="{self.current_note_id}">{content}</note>')
        self.current_note_id = None
        self.current_note = []


def clean_inline(xml: str) -> str:
    xml = re.sub(r"\s+", " ", xml)
    xml = re.sub(r"\s+([,.;:!?])", r"\1", xml)
    xml = re.sub(r"([«(])\s+", r"\1", xml)
    xml = re.sub(r"\s+([»)])", r"\1", xml)
    return xml.strip()


def content_fragment(html_text: str) -> str:
    start_marker = '<hr size=1 noshade>'
    start = html_text.find(start_marker)
    if start == -1:
        raise ValueError("Could not find IntraText content start marker.")
    fragment = html_text[start + len(start_marker) :]

    footer_match = re.search(
        r"<br\s+clear=all\s*/?><br\s*/?><center><hr\s+size=1\s+width=70%",
        fragment,
        flags=re.IGNORECASE,
    )
    if footer_match:
        fragment = fragment[: footer_match.start()]
    return fragment


def parse_page(path: Path) -> ParsedPage:
    html_text = path.read_text(encoding="iso-8859-1")
    parser = IntraTextContentParser()
    parser.feed(content_fragment(html_text))
    parser.close()
    return ParsedPage(blocks=merge_page_split_paragraphs(parser.blocks), notes=parser.notes)


def plain_text(xml: str) -> str:
    text = re.sub(r"<[^>]+>", "", xml)
    text = text.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
    return clean_inline(text)


def is_p(block: str) -> bool:
    return block.startswith("<p>") and block.endswith("</p>")


def p_inner(block: str) -> str:
    return block[3:-4] if is_p(block) else block


def is_pb(block: str) -> bool:
    return block.startswith("<pb ")


def strip_refs_for_boundary(xml: str) -> str:
    xml = re.sub(r"<ref\b[^>]*>.*?</ref>", "", xml)
    xml = re.sub(r"<[^>]+>", "", xml)
    xml = xml.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
    return clean_inline(xml)


def starts_continuation(xml: str) -> bool:
    text = strip_refs_for_boundary(xml)
    if not text:
        return False
    return text[0].islower() or text[0] in ",.;:)]»"


def ends_open(xml: str) -> bool:
    text = strip_refs_for_boundary(xml)
    if not text:
        return False
    return not re.search(r"[.!?…»”)\]]\s*$", text)


def merge_page_split_paragraphs(blocks: list[str]) -> list[str]:
    merged: list[str] = []
    i = 0
    while i < len(blocks):
        if (
            i + 2 < len(blocks)
            and is_p(blocks[i])
            and is_pb(blocks[i + 1])
            and is_p(blocks[i + 2])
            and (ends_open(blocks[i]) or starts_continuation(blocks[i + 2]))
        ):
            merged.append(f"<p>{p_inner(blocks[i])} {blocks[i + 1]} {p_inner(blocks[i + 2])}</p>")
            i += 3
            continue
        merged.append(blocks[i])
        i += 1
    return merged


def slug(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "div"


def div_open(div_type: str, xml_id: str | None = None, n: str | None = None, source: str | None = None) -> str:
    attrs = [f'type="{div_type}"']
    if xml_id:
        attrs.append(f'xml:id="{xml_id}"')
    if n:
        attrs.append(f'n="{escape(n, quote=True)}"')
    if source:
        attrs.append(f'source="{escape(source, quote=True)}"')
    return "<div " + " ".join(attrs) + ">"


def milestone_for(page: dict[str, Any]) -> str:
    page_id = Path(page["local_path"]).stem.lstrip("_")
    return (
        f'<milestone unit="intratext-page" xml:id="src-{page_id}" '
        f'n="{page["order"]}" source="{escape(page["source_url"], quote=True)}"/>'
    )


def append_notes(notes: list[str], page_notes: list[str]) -> None:
    notes.extend(page_notes)


def skip_duplicate_heading(block: str, title: str) -> bool:
    if not is_p(block):
        return False
    text = plain_text(block).rstrip(".")
    wanted = title.rstrip(".")
    return text == wanted or text.startswith(wanted)


def build_simple_div(page: dict[str, Any], parsed: ParsedPage, div_type: str, xml_id: str) -> str:
    blocks = [milestone_for(page)]
    title = escape(page["title"], quote=False)
    blocks.append(f"<head>{title}</head>")
    for block in parsed.blocks:
        if skip_duplicate_heading(block, page["title"]):
            continue
        blocks.append(block)
    return f'{div_open(div_type, xml_id=xml_id, source=page["source_url"])}\n      ' + "\n      ".join(blocks) + "\n    </div>"


def build_front_divs(pages: list[dict[str, Any]], parsed_pages: dict[str, ParsedPage]) -> str:
    divs: list[str] = []
    for page in pages[:2]:
        page_id = Path(page["local_path"]).stem.lstrip("_")
        divs.append(build_simple_div(page, parsed_pages[page_id], "editorial", f"front-{page_id}"))

    for page in pages[2:6]:
        page_id = Path(page["local_path"]).stem.lstrip("_")
        parsed = parsed_pages[page_id]
        if page_id != "p6":
            divs.append(build_simple_div(page, parsed, "frontMatter", f"front-{page_id}"))
            continue

        blocks: list[str] = [milestone_for(page), f"<head>{escape(page['title'], quote=False)}</head>"]
        in_prayer = False
        prayer_blocks: list[str] = []
        for block in parsed.blocks:
            text = plain_text(block)
            if skip_duplicate_heading(block, page["title"]):
                continue
            if text == "ORAZIONE ALLA B. VERGINE PER IMPETRAR BUONA MORTE":
                in_prayer = True
                prayer_blocks.append(f"<head>{p_inner(block)}</head>")
                continue
            if in_prayer:
                prayer_blocks.append(block)
            else:
                blocks.append(block)
        if prayer_blocks:
            blocks.append(div_open("prayer", xml_id="orazione-buona-morte") + "\n        " + "\n        ".join(prayer_blocks) + "\n      </div>")
        divs.append(f'{div_open("introduction", xml_id="front-p6", source=page["source_url"])}\n      ' + "\n      ".join(blocks) + "\n    </div>")

    return "<front>\n    " + "\n    ".join(divs) + "\n  </front>"


def process_sectioned_page(
    page: dict[str, Any],
    parsed: ParsedPage,
    div_type: str,
    xml_id: str,
    section_pattern: re.Pattern[str],
    subsection_types: dict[str, str] | None = None,
    skip_texts: set[str] | None = None,
) -> str:
    subsection_types = subsection_types or {"Esempio": "example", "Preghiera": "prayer"}
    skip_texts = skip_texts or set()
    out = [div_open(div_type, xml_id=xml_id, n=str(page["order"]), source=page["source_url"])]
    out.append(f"<head>{escape(page['title'], quote=False)}</head>")
    out.append(milestone_for(page))
    section_open = False
    subsection_open = False
    section_count = 0
    subsection_count = 0

    def close_subsection() -> None:
        nonlocal subsection_open
        if subsection_open:
            out.append("</div>")
            subsection_open = False

    def close_section() -> None:
        nonlocal section_open
        close_subsection()
        if section_open:
            out.append("</div>")
            section_open = False

    for block in parsed.blocks:
        text = plain_text(block)
        if text in skip_texts or skip_duplicate_heading(block, page["title"]):
            continue
        if is_p(block) and section_pattern.match(text):
            close_section()
            section_count += 1
            section_id = f"{xml_id}-sec-{section_count}"
            out.append(div_open("section", xml_id=section_id, n=str(section_count)))
            out.append(f"<head>{p_inner(block)}</head>")
            section_open = True
            continue

        matched_subsection = None
        if is_p(block):
            for prefix, sub_type in subsection_types.items():
                if text.startswith(prefix):
                    matched_subsection = sub_type
                    break
        if matched_subsection:
            close_subsection()
            subsection_count += 1
            sub_id = f"{xml_id}-{matched_subsection}-{subsection_count}"
            out.append(div_open(matched_subsection, xml_id=sub_id))
            out.append(f"<head>{p_inner(block)}</head>")
            subsection_open = True
            continue

        out.append(block)

    close_section()
    out.append("</div>")
    return "\n      ".join(out)


def build_part_one(pages: list[dict[str, Any]], parsed_pages: dict[str, ParsedPage]) -> str:
    divs = [div_open("part", xml_id="parte-prima", n="1"), "<head>Parte prima</head>"]
    for page in pages[6:16]:
        page_id = Path(page["local_path"]).stem.lstrip("_")
        divs.append(
            process_sectioned_page(
                page,
                parsed_pages[page_id],
                "chapter",
                f"parte-prima-{page_id}",
                re.compile(r"^§\s+"),
                skip_texts={"Parte prima"},
            )
        )
    page = pages[16]
    page_id = Path(page["local_path"]).stem.lstrip("_")
    divs.append(
        process_sectioned_page(
            page,
            parsed_pages[page_id],
            "prayers",
            "parte-prima-orazioni",
            re.compile(r"^Orazione\b|^Preghiera\b"),
            subsection_types={},
            skip_texts={"FINE DELLA PRIMA PARTE", "---------------"},
        )
    )
    divs.append("</div>")
    return "\n    ".join(divs)


def build_discorsi(page: dict[str, Any], parsed: ParsedPage) -> str:
    return process_sectioned_page(
        page,
        parsed,
        "sectionGroup",
        "parte-seconda-discorsi",
        re.compile(r"^DISCORSO\s+"),
        subsection_types={"Punto": "point", "Esempio": "example", "Preghiera": "prayer"},
        skip_texts={"Parte seconda.", "DISCORSI SULLE SETTE FESTE PRINCIPALI DI MARIA"},
    )


def build_examples_page(page: dict[str, Any], parsed: ParsedPage) -> str:
    return process_sectioned_page(
        page,
        parsed,
        "examples",
        "parte-seconda-esempi",
        re.compile(r"^\d+\.\s*(?:\*|\d+)?$"),
        subsection_types={},
    )


def build_prayers_page(page: dict[str, Any], parsed: ParsedPage) -> str:
    return process_sectioned_page(
        page,
        parsed,
        "prayers",
        "parte-seconda-orazioni",
        re.compile(
            r"^(Precatio|Orazione|In te spem|Non est fas|Tantummodo|Ave,|CORONELLA|Dedicazione|Madre di Dio|Vergine|O Signora|O Maria|Santa Maria|S'io amo|Iesus et Maria|Ad te clamamus|Domina rerum|Curre|Quis ad te)"
        ),
        subsection_types={},
    )


def build_part_two(pages: list[dict[str, Any]], parsed_pages: dict[str, ParsedPage]) -> str:
    divs = [div_open("part", xml_id="parte-seconda", n="2"), "<head>Parte seconda</head>"]
    builders = {
        "pi": build_discorsi,
        "pj": lambda page, parsed: process_sectioned_page(
            page,
            parsed,
            "sectionGroup",
            "parte-seconda-dolori",
            re.compile(r"^SUL DOLORE\s+"),
            subsection_types={"Esempio": "example", "Preghiera": "prayer"},
        ),
        "pk": lambda page, parsed: process_sectioned_page(
            page,
            parsed,
            "sectionGroup",
            "parte-seconda-virtu",
            re.compile(r"^§\s+"),
            subsection_types={},
        ),
        "pl": lambda page, parsed: process_sectioned_page(
            page,
            parsed,
            "sectionGroup",
            "parte-seconda-ossequi",
            re.compile(r"^OSSEQUIO\s+"),
            subsection_types={},
        ),
        "pm": lambda page, parsed: build_simple_div(page, parsed, "conclusion", "parte-seconda-conclusione"),
        "pn": build_examples_page,
        "po": build_prayers_page,
    }
    for page in pages[17:24]:
        page_id = Path(page["local_path"]).stem.lstrip("_")
        divs.append(builders[page_id](page, parsed_pages[page_id]))
    divs.append("</div>")
    return "\n    ".join(divs)


def build_back(notes: list[str]) -> str:
    return "<back>\n    <div type=\"notes\" xml:id=\"notes\">\n      <head>Note</head>\n      " + "\n      ".join(notes) + "\n    </div>\n  </back>"


def tei_header(manifest: dict[str, Any]) -> str:
    downloaded_at = escape(manifest["work"]["downloaded_at"])
    license_text = escape(manifest["work"]["license"])
    license_url = escape(manifest["work"]["license_url"])
    index_url = escape(manifest["work"]["index_url"])
    return f"""<teiHeader>
  <fileDesc>
    <titleStmt>
      <title>Le Glorie di Maria</title>
      <author>Alfonso Maria de Liguori</author>
      <respStmt>
        <resp>Digital source</resp>
        <name>IntraText Digital Library / EuloTech</name>
      </respStmt>
    </titleStmt>
    <publicationStmt>
      <p>Generated locally for the Glorie di Maria digital edition project.</p>
      <availability>
        <licence target="{license_url}">{license_text}</licence>
      </availability>
    </publicationStmt>
    <sourceDesc>
      <bibl>
        S. Alfonso Maria de Liguori, <title>OPERE ASCETICHE</title>, voll. VI e VII,
        CSSR, Roma 1937-1938; digital text from IntraText, {index_url}.
      </bibl>
    </sourceDesc>
  </fileDesc>
  <encodingDesc>
    <p>Semantic conversion from downloaded IntraText HTML. Text pages use the hidden-concordance-link variant (__P*.HTM). IntraText page boundaries are preserved as milestones.</p>
  </encodingDesc>
  <revisionDesc>
    <change when="{downloaded_at}">Converted from local IntraText raw HTML archive.</change>
  </revisionDesc>
</teiHeader>"""


def build_tei(manifest: dict[str, Any]) -> str:
    parsed_pages: dict[str, ParsedPage] = {}
    all_notes: list[str] = []
    for page in manifest["pages"]:
        local_path = Path(page["local_path"])
        parsed = parse_page(local_path)
        page_id = local_path.stem.lstrip("_")
        parsed_pages[page_id] = parsed
        append_notes(all_notes, parsed.notes)

    pages = manifest["pages"]
    front = build_front_divs(pages, parsed_pages)
    body = "<body>\n    " + build_part_one(pages, parsed_pages) + "\n    " + build_part_two(pages, parsed_pages) + "\n  </body>"
    back = build_back(all_notes)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<TEI xmlns="{TEI_NS}" xml:lang="it">
  {tei_header(manifest)}
  <text>
  {front}
  {body}
  {back}
  </text>
</TEI>
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--out", type=Path, default=OUT_FILE)
    args = parser.parse_args()

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    tei = build_tei(manifest)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(tei, encoding="utf-8")

    ElementTree.parse(args.out)
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
