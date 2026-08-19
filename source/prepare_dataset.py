"""Tek seferlik ön işleme: ham Blender Stack Exchange veri dökümünü
(dataset_raw/Posts.xml, resmi Stack Exchange Data Dump'tan) ingest
pipeline'ının okuduğu temiz, sınırlandırılmış bir JSON dosyasına çevirir.

Kullanım:
    python -m source.prepare_dataset

dataset_raw/Posts.xml'in önceden var olması bekleniyor (önce 7z arşivini
indirip çıkarın -- bkz. README.md).

Sadece standart kütüphane kullanılıyor (xml.etree, html.parser), bu yüzden
projeye yeni bir pip bağımlılığı eklemiyor.
"""
import json
import sys
from html.parser import HTMLParser
from xml.etree import ElementTree as ET

import source.config as config


MIN_QUESTION_SCORE = 5
MAX_TUTORIALS = 1500
MAX_QUESTION_CHARS = 1200
MAX_ANSWER_CHARS = 3000


class _HTMLToText(HTMLParser):
    """Stack Exchange gönderi gövdesi HTML'ini düz metne çeviren minimal bir sınıf."""

    BLOCK_TAGS = {"p", "div", "blockquote", "pre", "ul", "ol", "h1", "h2", "h3"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self._parts = []

    def handle_starttag(self, tag, attrs):
        if tag == "li":
            self._parts.append("\n- ")
        elif tag == "br":
            self._parts.append("\n")
        elif tag in self.BLOCK_TAGS:
            self._parts.append("\n")

    def handle_endtag(self, tag):
        if tag in self.BLOCK_TAGS:
            self._parts.append("\n")

    def handle_data(self, data):
        self._parts.append(data)

    def text(self):
        collapsed = "".join(self._parts)
        lines = [line.strip() for line in collapsed.splitlines()]
        lines = [line for line in lines if line]
        return "\n".join(lines)


def html_to_text(html):
    parser = _HTMLToText()
    parser.feed(html or "")
    return parser.text()


def truncate(text, max_chars):
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rstrip() + "..."


def parse_tags(raw_tags):
    return [t for t in (raw_tags or "").split("|") if t]


def collect_questions(xml_path):
    """1. geçiş: kriterleri karşılayan sorular, post Id'lerine göre anahtarlanmış."""
    questions = {}
    for _, elem in ET.iterparse(xml_path, events=("end",)):
        if elem.tag != "row":
            continue
        attrib = elem.attrib
        if attrib.get("PostTypeId") == "1":
            accepted_id = attrib.get("AcceptedAnswerId")
            score = int(attrib.get("Score", "0"))
            if accepted_id and score >= MIN_QUESTION_SCORE:
                questions[attrib["Id"]] = {
                    "id": attrib["Id"],
                    "accepted_answer_id": accepted_id,
                    "title": attrib.get("Title", ""),
                    "tags": parse_tags(attrib.get("Tags")),
                    "question_html": attrib.get("Body", ""),
                    "score": score,
                }
        elem.clear()
    return questions


def collect_answers(xml_path, needed_ids):
    """2. geçiş: sadece gerçekten ihtiyacımız olan kabul edilmiş cevap gövdeleri."""
    answers = {}
    for _, elem in ET.iterparse(xml_path, events=("end",)):
        if elem.tag != "row":
            continue
        attrib = elem.attrib
        if attrib.get("PostTypeId") == "2" and attrib.get("Id") in needed_ids:
            answers[attrib["Id"]] = attrib.get("Body", "")
        elem.clear()
    return answers


def build_dataset(xml_path):
    print(f"1/2. geçiş: {xml_path} içindeki sorular taranıyor ...")
    questions = collect_questions(xml_path)
    print(f"  skoru >= {MIN_QUESTION_SCORE} ve kabul edilmiş cevabı olan {len(questions)} soru bulundu")

    top_questions = sorted(
        questions.values(), key=lambda q: q["score"], reverse=True
    )[:MAX_TUTORIALS]
    needed_ids = {q["accepted_answer_id"] for q in top_questions}

    print(f"2/2. geçiş: {len(needed_ids)} kabul edilmiş cevap getiriliyor ...")
    answers = collect_answers(xml_path, needed_ids)

    records = []
    for q in top_questions:
        answer_html = answers.get(q["accepted_answer_id"])
        if not answer_html:
            continue
        records.append({
            "id": q["id"],
            "title": q["title"],
            "tags": q["tags"],
            "question": truncate(html_to_text(q["question_html"]), MAX_QUESTION_CHARS),
            "answer": truncate(html_to_text(answer_html), MAX_ANSWER_CHARS),
            "score": q["score"],
        })
    return records


def main():
    if not config.POSTS_XML_PATH.exists():
        print(
            f"{config.POSTS_XML_PATH} bulunamadı. Önce "
            "dataset_raw/blender.stackexchange.com.7z arşivini indirip çıkarın "
            "(bkz. README.md).",
            file=sys.stderr,
        )
        return 1

    records = build_dataset(config.POSTS_XML_PATH)
    config.DATASET_JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(config.DATASET_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

    print(f"{len(records)} rehber {config.DATASET_JSON_PATH} konumuna yazıldı")
    return 0


if __name__ == "__main__":
    sys.exit(main())
