#!/usr/bin/env python3
"""Download the Deuterocanonical books (Greek Septuagint, Swete edition).

Source: nathans/lxx-swete (Swete's Septuagint, word-per-line format).

The Deuterocanonical books (Catholic canon) not in the Hebrew Tanakh:
  Tobit, Judith, Wisdom of Solomon, Sirach (Ecclesiasticus), Baruch,
  Letter of Jeremiah, 1 Maccabees, 2 Maccabees, and the Greek additions
  to Esther and Daniel (Susanna, Bel and the Dragon).

Output: raw/deutero/*.txt
"""
import os, time, urllib.request, urllib.error

BASE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(BASE, 'raw', 'deutero')
os.makedirs(RAW, exist_ok=True)

LXX_BASE = 'https://raw.githubusercontent.com/nathans/lxx-swete/master/data'

# (source filename, canonical book name)
DEUTERO_BOOKS = [
    ('21.Tobias.txt', 'Tobit'),
    ('20.Judith.txt', 'Judith'),
    ('33.Sapientia_Salomonis.txt', 'Wisdom of Solomon'),
    ('34.Ecclesiasticus.txt', 'Sirach'),
    ('50.Baruch.txt', 'Baruch'),
    ('52.Epistula_Jeremiae.txt', 'Letter of Jeremiah'),
    ('23.Machabaeorum_i.txt', '1 Maccabees'),
    ('24.Machabaeorum_ii.txt', '2 Maccabees'),
    # Greek additions to Esther and Daniel
    ('19.Esther.txt', 'Esther (Greek)'),
    ('54.Susanna_translatio_Graeca.txt', 'Susanna'),
    ('58.Bel_et_Draco_translatio_Graeca.txt', 'Bel and the Dragon'),
    ('56.Daniel_translatio_Graeca.txt', 'Daniel (Greek)'),
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
    for src, name in DEUTERO_BOOKS:
        out = os.path.join(RAW, src)
        if os.path.exists(out) and os.path.getsize(out) > 1000:
            ok += 1
            continue
        url = f'{LXX_BASE}/{src}'
        try:
            data = fetch(url)
            with open(out, 'wb') as f:
                f.write(data)
            ok += 1
        except Exception as e:
            fail += 1
            print(f"FAIL {src}: {e}")
        time.sleep(0.1)
    print(f"DONE: ok={ok}, fail={fail}, total={len(DEUTERO_BOOKS)}")


if __name__ == '__main__':
    main()
