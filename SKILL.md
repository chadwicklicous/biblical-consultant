---
name: biblical-consultant
description: "Answer Bible questions from the original Hebrew and Greek."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, macos, linux]
metadata:
  hermes:
    tags: [bible, hebrew, greek, old-testament, new-testament, exegesis, vector-search]
    category: research
---

# Biblical Consultant

Answer questions about the Bible **from the original languages** — the Hebrew Old Testament (Westminster Leningrad Codex), the Greek New Testament (SBL Greek New Testament), and the Deuterocanonical books (Swete Septuagint) — with exact book/chapter/verse citations, not from a translation or the model's recollection.

## When to Use

- User asks a question about a biblical passage, theme, word, or concept
- User wants a verse located, a Hebrew/Greek word examined, or a citation verified
- User is doing exegesis, study, or writing and needs the original-language text with a precise reference

## Setup (one-time — the agent runs this, not the user)

When the user first asks to use the Biblical consultant, **the agent performs this setup autonomously**. The user should not have to run any commands, install any programs, or understand any of this. The user just talks to the agent in plain English.

The pipeline scripts are bundled in this skill's `scripts/` directory:
[`scripts/bc_download.py`](scripts/bc_download.py),
[`scripts/bc_download_deutero.py`](scripts/bc_download_deutero.py),
[`scripts/bc_extract.py`](scripts/bc_extract.py),
[`scripts/bc_extract_deutero.py`](scripts/bc_extract_deutero.py), and
[`scripts/bc_index.py`](scripts/bc_index.py).

Resolve the skill's directory (the directory containing this `SKILL.md`) and run
everything from there — no separate clone or download is needed.

1. **Install Python dependencies** (pinned version):
   ```bash
   pip install "chromadb==1.5.9"
   ```

2. **Install Ollama if it is not already present.** Check first:
   ```bash
   ollama --version
   ```
   If that fails, install it for the user's platform:
   - **Windows:** download and run the installer from https://ollama.com/download/OllamaSetup.exe
   - **macOS:** download and run https://ollama.com/download/Ollama-darwin.zip
   - **Linux:** download the installer from https://ollama.com/download/linux and run it, or use your package manager (e.g. `sudo apt install ollama` on Debian/Ubuntu).
   Then start the Ollama service (on Windows/macOS the installer launches it; on
   Linux run `ollama serve` in the background).

3. **Pull the embedding model** — `bge-m3` (multilingual, required for Hebrew/Greek):
   ```bash
   ollama pull bge-m3
   ```

4. **Build the corpus and index.** This downloads ~78 books and embeds 35,793
   verses. It takes a few hours on CPU and is **resumable** — if it is
   interrupted, re-run `scripts/bc_index.py` and it continues from where it stopped.
   ```bash
   cd <skill-dir>/scripts
   python bc_download.py          # Hebrew OT + Greek NT
   python bc_download_deutero.py  # Deuterocanonical books
   python bc_extract.py           # extract Hebrew + Greek verses
   python bc_extract_deutero.py   # extract deuterocanonical verses
   python bc_index.py             # build the vector index
   ```

5. **Verify** the setup works:
   ```bash
   python bc_index.py --query "in the beginning God created" --k 3
   ```
   If it returns verses with citations, the consultant is ready.

After setup, the user asks questions in natural language and the agent retrieves
the relevant Hebrew/Greek verses with citations.

## Query Workflow

### 1. Semantic retrieval

```bash
cd <skill-dir>/scripts
python bc_index.py --query "<question, in Hebrew, Greek, or English>" --k 5
```

bge-m3 is multilingual, so English queries match Hebrew/Greek text. Returns the
top-k verses with exact citations. For a broader sweep, use `--k 10`.

### 2. Read the actual text

The query returns the verse text. Read it carefully. If you need the full verse
(the query truncates to 300 chars), grep the TSV:

```bash
grep -F "Genesis 1:1" <skill-dir>/scripts/text/01_genesis.tsv
```

### 3. Answer from the source

- Quote the **original Hebrew or Greek** verse.
- Give the **exact citation** (e.g. `Genesis 1:1`, `Matthew 1:1`).
- Explain the passage in the user's language, but anchor every claim in the quoted text.
- Note the original-language word where relevant (e.g. Hebrew *bara*, Greek *logos*).

## Citation format

| Form | Meaning |
|------|---------|
| `Genesis 1:1` | Hebrew OT, book + chapter:verse |
| `Isaiah 64:1` | note: mislabeled "NaN" in source; extractor corrects it |
| `Matthew 1:1` | Greek NT, full book name + chapter:verse |
| `Tobit 1:1` | Deuterocanonical, Greek LXX, book + chapter:verse |

## Pitfalls

- **Don't answer from memory or from a translation.** Always retrieve and quote the original Hebrew/Greek. The whole point is citation-grounded answers in the original languages.
- **The index build is resumable.** If `bc_index.py` dies partway, re-run it — it resumes from the last indexed count.
- **Ollama must be running** for embeddings (`ollama serve`). Model: `bge-m3` (multilingual — required for Hebrew/Greek; nomic-embed-text does NOT handle these scripts well).
- **Long verses** are truncated to 6000 chars before embedding.
- **The Hebrew text includes cantillation marks** (Masoretic accents). These are part of the text and should be preserved when quoting.

## Verification

1. Run a query and confirm it returns verses with valid citations.
2. Grep the TSV to confirm the full verse text matches the citation.
3. Answer a test question and confirm every claim is anchored in a quoted Hebrew/Greek verse.
