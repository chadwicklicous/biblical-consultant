#!/usr/bin/env python3
"""Extract citation-tagged verses from the Deuterocanonical books (Swete LXX).

The Swete LXX format is word-per-line:  "20.1.1 ΕΤΟΥΣ"  = book.chapter.verse word.
We group words by (chapter, verse) and join them into full verses.

Output: text/<book>.tsv  — one verse per line:  CITATION\tTEXT
"""
import os, re

BASE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(BASE, 'raw', 'deutero')
TXT = os.path.join(BASE, 'text')
os.makedirs(TXT, exist_ok=True)

# Map source filename -> canonical book name
BOOK_NAMES = {
    '21.Tobias.txt': 'Tobit',
    '20.Judith.txt': 'Judith',
    '33.Sapientia_Salomonis.txt': 'Wisdom of Solomon',
    '34.Ecclesiasticus.txt': 'Sirach',
    '50.Baruch.txt': 'Baruch',
    '52.Epistula_Jeremiae.txt': 'Letter of Jeremiah',
    '23.Machabaeorum_i.txt': '1 Maccabees',
    '24.Machabaeorum_ii.txt': '2 Maccabees',
    '19.Esther.txt': 'Esther (Greek)',
    '54.Susanna_translatio_Graeca.txt': 'Susanna',
    '58.Bel_et_Draco_translatio_Graeca.txt': 'Bel and the Dragon',
    '56.Daniel_translatio_Graeca.txt': 'Daniel (Greek)',
}

# Line format: "20.1.1 ΕΤΟΥΣ"  (book.chapter.verse word)
# The first number is the Swete book number (ignored — we know the book from
# the filename); the second is chapter, the third is verse.
LINE_RE = re.compile(r'^\d+\.(\d+)\.(\d+)\s+(.+)$')


def extract(fname):
    path = os.path.join(RAW, fname)
    if not os.path.exists(path):
        return []
    book = BOOK_NAMES.get(fname, fname.replace('.txt', ''))

    with open(path, encoding='utf-8') as f:
        lines = f.readlines()

    # Group words by (chapter, verse)
    verses = {}  # (ch, v) -> list of words
    for line in lines:
        line = line.strip()
        m = LINE_RE.match(line)
        if not m:
            continue
        ch, v, word = m.group(1), m.group(2), m.group(3)
        key = (ch, v)
        verses.setdefault(key, []).append(word)

    # Join into full verses, sorted by chapter then verse
    result = []
    for (ch, v) in sorted(verses.keys(), key=lambda x: (int(x[0]), int(x[1]))):
        text = ' '.join(verses[(ch, v)]).strip()
        if text:
            result.append((f'{book} {ch}:{v}', text))
    return result


def main():
    total = 0
    for fname in sorted(os.listdir(RAW)):
        if not fname.endswith('.txt'):
            continue
        verses = extract(fname)
        if not verses:
            continue
        out = os.path.join(TXT, fname.replace('.txt', '.tsv'))
        with open(out, 'w', encoding='utf-8') as f:
            for cit, text in verses:
                f.write(f'{cit}\t{text}\n')
        total += len(verses)
    print(f'Extracted {total} deuterocanonical verses')


if __name__ == '__main__':
    main()
