#!/usr/bin/env python3
"""Download the Hebrew Old Testament (WLC) and Greek New Testament (SBLGNT).

Sources:
  - Hebrew OT: wjbaker2025/hebrew-holy-tanakh (word-level JSON, Westminster
    Leningrad Codex, with Strong's numbers + morphology + English gloss)
  - Greek NT: Faithlife/SBLGNT (per-book text files, SBL Greek New Testament)

Output:
  raw/hebrew/*.json   (39 books)
  raw/greek/*.txt     (27 books)

Resumable: skips files already downloaded.
"""
import os, json, time, urllib.request, urllib.error

BASE = os.path.dirname(os.path.abspath(__file__))
RAW_HEB = os.path.join(BASE, 'raw', 'hebrew')
RAW_GRK = os.path.join(BASE, 'raw', 'greek')
os.makedirs(RAW_HEB, exist_ok=True)
os.makedirs(RAW_GRK, exist_ok=True)

HEB_BASE = 'https://raw.githubusercontent.com/wjbaker2025/hebrew-holy-tanakh/main/Tanakh'
GRK_BASE = 'https://raw.githubusercontent.com/Faithlife/SBLGNT/master/data/sblgnt/text'

# Hebrew OT: (section_path, filename)
HEBREW_BOOKS = [
    # Torah
    ('1.%20Torah%20-%20Instructions', '01_genesis.json'),
    ('1.%20Torah%20-%20Instructions', '02_exodus.json'),
    ('1.%20Torah%20-%20Instructions', '03_leviticus.json'),
    ('1.%20Torah%20-%20Instructions', '04_numbers.json'),
    ('1.%20Torah%20-%20Instructions', '05_deuteronomy.json'),
    # Former Prophets
    ('2.%20Nevi%27im%20-%20Prophets/1.%20Former%20Prophets', '06_joshua.json'),
    ('2.%20Nevi%27im%20-%20Prophets/1.%20Former%20Prophets', '07_judges.json'),
    ('2.%20Nevi%27im%20-%20Prophets/1.%20Former%20Prophets', '08_1_samuel.json'),
    ('2.%20Nevi%27im%20-%20Prophets/1.%20Former%20Prophets', '09_2_samuel.json'),
    ('2.%20Nevi%27im%20-%20Prophets/1.%20Former%20Prophets', '10_1_kings.json'),
    ('2.%20Nevi%27im%20-%20Prophets/1.%20Former%20Prophets', '11_2_kings.json'),
    # Latter Prophets
    ('2.%20Nevi%27im%20-%20Prophets/2.%20Latter%20Prophets', '12_isaiah.json'),
    ('2.%20Nevi%27im%20-%20Prophets/2.%20Latter%20Prophets', '13_jeremiah.json'),
    ('2.%20Nevi%27im%20-%20Prophets/2.%20Latter%20Prophets', '14_ezekiel.json'),
    # Minor Prophets
    ('2.%20Nevi%27im%20-%20Prophets/3.%20Minor%20Prophets', '15_hosea.json'),
    ('2.%20Nevi%27im%20-%20Prophets/3.%20Minor%20Prophets', '16_joel.json'),
    ('2.%20Nevi%27im%20-%20Prophets/3.%20Minor%20Prophets', '17_amos.json'),
    ('2.%20Nevi%27im%20-%20Prophets/3.%20Minor%20Prophets', '18_obadiah.json'),
    ('2.%20Nevi%27im%20-%20Prophets/3.%20Minor%20Prophets', '19_jonah.json'),
    ('2.%20Nevi%27im%20-%20Prophets/3.%20Minor%20Prophets', '20_micah.json'),
    ('2.%20Nevi%27im%20-%20Prophets/3.%20Minor%20Prophets', '21_nahum.json'),
    ('2.%20Nevi%27im%20-%20Prophets/3.%20Minor%20Prophets', '22_habakkuk.json'),
    ('2.%20Nevi%27im%20-%20Prophets/3.%20Minor%20Prophets', '23_zephaniah.json'),
    ('2.%20Nevi%27im%20-%20Prophets/3.%20Minor%20Prophets', '24_haggai.json'),
    ('2.%20Nevi%27im%20-%20Prophets/3.%20Minor%20Prophets', '25_zechariah.json'),
    ('2.%20Nevi%27im%20-%20Prophets/3.%20Minor%20Prophets', '26_malachi.json'),
    # Ketuvim
    ('3.%20Ketuvim%20-%20Writings', '27_psalms.json'),
    ('3.%20Ketuvim%20-%20Writings', '28_proverbs.json'),
    ('3.%20Ketuvim%20-%20Writings', '29_job.json'),
    ('3.%20Ketuvim%20-%20Writings', '30_song_of_solomon.json'),
    ('3.%20Ketuvim%20-%20Writings', '31_ruth.json'),
    ('3.%20Ketuvim%20-%20Writings', '32_lamentations.json'),
    ('3.%20Ketuvim%20-%20Writings', '33_ecclesiastes.json'),
    ('3.%20Ketuvim%20-%20Writings', '34_esther.json'),
    ('3.%20Ketuvim%20-%20Writings', '35_daniel.json'),
    ('3.%20Ketuvim%20-%20Writings', '36_ezra.json'),
    ('3.%20Ketuvim%20-%20Writings', '37_nehemiah.json'),
    ('3.%20Ketuvim%20-%20Writings', '38_1_chronicles.json'),
    ('3.%20Ketuvim%20-%20Writings', '39_2_chronicles.json'),
]

# Greek NT: 27 books
GREEK_BOOKS = [
    'Matt', 'Mark', 'Luke', 'John', 'Acts', 'Rom', '1Cor', '2Cor', 'Gal',
    'Eph', 'Phil', 'Col', '1Thess', '2Thess', '1Tim', '2Tim', 'Titus',
    'Phlm', 'Heb', 'Jas', '1Pet', '2Pet', '1John', '2John', '3John', 'Jude',
    'Rev',
]

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'


def fetch(url, retries=4):
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read()
        except Exception:
            if attempt == retries - 1:
                raise
            time.sleep(2 * (attempt + 1))


def main():
    ok, fail = 0, 0

    # Hebrew OT
    for section, fname in HEBREW_BOOKS:
        out = os.path.join(RAW_HEB, fname)
        if os.path.exists(out) and os.path.getsize(out) > 1000:
            ok += 1
            continue
        url = f'{HEB_BASE}/{section}/{fname}'
        try:
            data = fetch(url)
            with open(out, 'wb') as f:
                f.write(data)
            ok += 1
        except Exception as e:
            fail += 1
            print(f"FAIL {fname}: {e}")
        time.sleep(0.1)

    # Greek NT
    for book in GREEK_BOOKS:
        fname = f'{book}.txt'
        out = os.path.join(RAW_GRK, fname)
        if os.path.exists(out) and os.path.getsize(out) > 1000:
            ok += 1
            continue
        url = f'{GRK_BASE}/{fname}'
        try:
            data = fetch(url)
            with open(out, 'wb') as f:
                f.write(data)
            ok += 1
        except Exception as e:
            fail += 1
            print(f"FAIL {fname}: {e}")
        time.sleep(0.1)

    print(f"DONE: ok={ok}, fail={fail}, total={len(HEBREW_BOOKS) + len(GREEK_BOOKS)}")


if __name__ == '__main__':
    main()
