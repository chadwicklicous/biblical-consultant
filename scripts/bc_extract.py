#!/usr/bin/env python3
"""Extract citation-tagged verses from Hebrew OT (JSON) and Greek NT (text).

Output: text/<book>.tsv  — one verse per line:  CITATION\tTEXT

Hebrew: joins word-level tokens into full verses (with cantillation marks).
Greek:  already verse-per-line ("Matt 1:1\tΒίβλος γενέσεως...").

Citation format:
  Hebrew: "Genesis 1:1"  (English book name, chapter:verse)
  Greek:  "Matt 1:1"     (SBLGNT abbreviation, chapter:verse)
"""
import os, json, re

BASE = os.path.dirname(os.path.abspath(__file__))
RAW_HEB = os.path.join(BASE, 'raw', 'hebrew')
RAW_GRK = os.path.join(BASE, 'raw', 'greek')
TXT = os.path.join(BASE, 'text')
os.makedirs(TXT, exist_ok=True)

# Map Hebrew JSON filename -> English book name
HEB_BOOK_NAMES = {
    '01_genesis': 'Genesis', '02_exodus': 'Exodus', '03_leviticus': 'Leviticus',
    '04_numbers': 'Numbers', '05_deuteronomy': 'Deuteronomy',
    '06_joshua': 'Joshua', '07_judges': 'Judges', '08_1_samuel': '1 Samuel',
    '09_2_samuel': '2 Samuel', '10_1_kings': '1 Kings', '11_2_kings': '2 Kings',
    '12_isaiah': 'Isaiah', '13_jeremiah': 'Jeremiah', '14_ezekiel': 'Ezekiel',
    '15_hosea': 'Hosea', '16_joel': 'Joel', '17_amos': 'Amos',
    '18_obadiah': 'Obadiah', '19_jonah': 'Jonah', '20_micah': 'Micah',
    '21_nahum': 'Nahum', '22_habakkuk': 'Habakkuk', '23_zephaniah': 'Zephaniah',
    '24_haggai': 'Haggai', '25_zechariah': 'Zechariah', '26_malachi': 'Malachi',
    '27_psalms': 'Psalms', '28_proverbs': 'Proverbs', '29_job': 'Job',
    '30_song_of_solomon': 'Song of Solomon', '31_ruth': 'Ruth',
    '32_lamentations': 'Lamentations', '33_ecclesiastes': 'Ecclesiastes',
    '34_esther': 'Esther', '35_daniel': 'Daniel', '36_ezra': 'Ezra',
    '37_nehemiah': 'Nehemiah', '38_1_chronicles': '1 Chronicles',
    '39_2_chronicles': '2 Chronicles',
}

# Map SBLGNT abbreviation -> full book name
GRK_BOOK_NAMES = {
    'Matt': 'Matthew', 'Mark': 'Mark', 'Luke': 'Luke', 'John': 'John',
    'Acts': 'Acts', 'Rom': 'Romans', '1Cor': '1 Corinthians',
    '2Cor': '2 Corinthians', 'Gal': 'Galatians', 'Eph': 'Ephesians',
    'Phil': 'Philippians', 'Col': 'Colossians', '1Thess': '1 Thessalonians',
    '2Thess': '2 Thessalonians', '1Tim': '1 Timothy', '2Tim': '2 Timothy',
    'Titus': 'Titus', 'Phlm': 'Philemon', 'Heb': 'Hebrews', 'Jas': 'James',
    '1Pet': '1 Peter', '2Pet': '2 Peter', '1John': '1 John', '2John': '2 John',
    '3John': '3 John', 'Jude': 'Jude', 'Rev': 'Revelation',
}


def extract_hebrew(fname):
    """Extract verses from a Hebrew JSON file. Returns list of (citation, text)."""
    path = os.path.join(RAW_HEB, fname)
    if not os.path.exists(path):
        return []
    with open(path, encoding='utf-8') as f:
        data = json.load(f)

    # The JSON has one top-level key (the book name)
    book_key = list(data.keys())[0]
    book = HEB_BOOK_NAMES.get(fname.replace('.json', ''), book_key)
    chapters = data[book_key].get('chapters', {})

    verses = []
    for ch_num in sorted(chapters.keys(), key=lambda x: int(x) if x.isdigit() else 0):
        ch = chapters[ch_num]
        for v_num in sorted(ch.keys(), key=lambda x: int(x) if x.isdigit() else 0):
            words = ch[v_num]
            # Join the "hebrew" field of each word token
            text = ' '.join(w.get('hebrew', '') for w in words).strip()
            if text:
                # Data quirk: Isaiah 64:1 is mislabeled "NaN" in the source.
                # Treat a non-numeric verse key as verse 1.
                verse_ref = v_num if v_num.isdigit() else '1'
                verses.append((f'{book} {ch_num}:{verse_ref}', text))
    return verses


def extract_greek(fname):
    """Extract verses from a Greek SBLGNT text file. Returns list of (citation, text)."""
    path = os.path.join(RAW_GRK, fname)
    if not os.path.exists(path):
        return []
    with open(path, encoding='utf-8') as f:
        content = f.read()

    abbr = fname.replace('.txt', '')
    book = GRK_BOOK_NAMES.get(abbr, abbr)

    verses = []
    for line in content.splitlines():
        line = line.strip()
        if not line or '\t' not in line:
            continue
        ref, text = line.split('\t', 1)
        # ref is like "Matt 1:1" — convert to full book name
        m = re.match(r'^[A-Za-z0-9]+\s+(\d+):(\d+)$', ref)
        if m:
            citation = f'{book} {m.group(1)}:{m.group(2)}'
        else:
            citation = f'{book} {ref}'
        text = text.strip()
        if text:
            verses.append((citation, text))
    return verses


def main():
    total = 0

    # Hebrew OT
    for fname in sorted(os.listdir(RAW_HEB)):
        if not fname.endswith('.json'):
            continue
        verses = extract_hebrew(fname)
        if not verses:
            continue
        out = os.path.join(TXT, fname.replace('.json', '.tsv'))
        with open(out, 'w', encoding='utf-8') as f:
            for cit, text in verses:
                f.write(f'{cit}\t{text}\n')
        total += len(verses)

    # Greek NT
    for fname in sorted(os.listdir(RAW_GRK)):
        if not fname.endswith('.txt'):
            continue
        verses = extract_greek(fname)
        if not verses:
            continue
        out = os.path.join(TXT, fname.replace('.txt', '.tsv'))
        with open(out, 'w', encoding='utf-8') as f:
            for cit, text in verses:
                f.write(f'{cit}\t{text}\n')
        total += len(verses)

    print(f'Extracted {total} verses')


if __name__ == '__main__':
    main()
