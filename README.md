# Biblical Consultant

A citation-grounded consultant for the Bible in its **original languages**. Builds a semantic-search index over the Hebrew Old Testament (Westminster Leningrad Codex), the Greek New Testament (SBL Greek New Testament), and the Deuterocanonical books (Swete Septuagint), and answers questions **from the original Hebrew and Greek with exact book/chapter/verse citations** — not from a translation or a model's recollection.

## What it does

1. Downloads the complete Bible in its original languages:
   - **Hebrew OT** (39 books) — Westminster Leningrad Codex, with cantillation marks
   - **Greek NT** (27 books) — SBL Greek New Testament
   - **Deuterocanonical** (12 books) — Swete Septuagint: Tobit, Judith, Wisdom of Solomon, Sirach, Baruch, Letter of Jeremiah, 1–2 Maccabees, and the Greek additions to Esther and Daniel
2. Extracts 35,793 verses, each tagged with its exact citation (e.g. `Genesis 1:1`, `Matthew 1:1`, `Tobit 1:1`).
3. Builds a ChromaDB vector index for semantic search.
4. Answers questions by retrieving the relevant Hebrew/Greek verses with citations.

## Two ways to use it

### For non-technical users (recommended): let your AI agent do the work

If you use **Hermes Agent** (or a similar AI agent), you don't need to run any commands. Just:

1. Install the skill:
   ```bash
   hermes skills install https://raw.githubusercontent.com/chadwicklicous/biblical-consultant/main/SKILL.md
   ```
   (or copy this repo's `SKILL.md` + `scripts/` into your agent's skills folder)
2. Say: *"Set up the Biblical consultant."*

Your agent reads the skill, installs the dependencies, downloads the corpus, builds the index, and verifies it — all autonomously. Then you ask questions in plain English and it answers from the original Hebrew/Greek with exact citations.

The skill is **self-contained**: the scripts are bundled in the skill's own `scripts/` directory, so the agent runs everything from there — no separate clone or download. The skill's **Setup** section is written as instructions *for the agent to execute*, so the user never touches a terminal.

### For technical users: run it directly

The pipeline is standalone Python. See the Quick start below.

## Requirements

- **Python 3.9+** (stdlib only for the pipeline; `chromadb` for the index)
- **ChromaDB** — the vector database. Installed via `pip install "chromadb==1.5.9"` (in `requirements.txt`). No separate server needed; it runs embedded.
- **Ollama** — the embedding provider (free, local, no API key). Pull the `bge-m3` model with `ollama pull bge-m3`. This model is **multilingual** and is required for Hebrew/Greek.
- **Hermes Agent** (optional) — to use the bundled `biblical-consultant` skill that documents the query-and-answer workflow. The pipeline itself is standalone Python and works without Hermes.

### What is NOT required

- **Obsidian is not required.** The tool is pure Python + ChromaDB + Ollama. It does not download or depend on Obsidian, or any other note-taking app.
- **No API keys** — Ollama is free and runs entirely on your machine.
- **No database server** — ChromaDB runs embedded, storing its index in a local directory.

## Quick start

```bash
# 1. Install dependencies
pip install "chromadb==1.5.9"

# 2. Pull the embedding model (multilingual, for Hebrew/Greek)
ollama pull bge-m3

# 3. Build the corpus (downloads ~78 books, extracts verses)
cd scripts
python bc_download.py          # Hebrew OT + Greek NT
python bc_download_deutero.py  # Deuterocanonical books
python bc_extract.py           # extract Hebrew + Greek verses
python bc_extract_deutero.py   # extract deuterocanonical verses

# 4. Build the vector index (embeds 35,793 verses)
python bc_index.py

# 5. Query
python bc_index.py --query "in the beginning God created" --k 5
```

The index build takes a few hours on CPU (it embeds 35k verses). It is **resumable** — re-run `bc_index.py` and it continues from where it stopped.

## Using with Hermes Agent

This repository **is** a Hermes skill — `SKILL.md` at the root, with the pipeline scripts bundled in `scripts/`. Install it with:

```bash
hermes skills install https://raw.githubusercontent.com/chadwicklicous/biblical-consultant/main/SKILL.md
```

The skill's **Setup** section tells the agent to run the full pipeline autonomously from the skill's own `scripts/` directory — the user just says "set up the Biblical consultant" and then asks questions in plain English. The agent retrieves verses with `bc_index.py --query`, reads the full Hebrew/Greek, and answers from the source with exact citations.

## How it works

```
openscriptures / Faithlife / nathans (source repos)
        │  bc_download.py + bc_download_deutero.py
        ▼
   raw/hebrew/*.json  raw/greek/*.txt  raw/deutero/*.txt
        │  bc_extract.py + bc_extract_deutero.py
        ▼
   text/*.tsv   (35,793 citation-tagged verses)
        │  bc_index.py  (embed with bge-m3 + store in ChromaDB)
        ▼
   chroma/  (vector index, collection "biblical_corpus")
        │  bc_index.py --query "..."
        ▼
   top-k verses with exact book/chapter/verse citations
```

## Citation format

| Form | Meaning |
|------|---------|
| `Genesis 1:1` | Hebrew OT, book + chapter:verse |
| `Matthew 1:1` | Greek NT, full book name + chapter:verse |
| `Tobit 1:1` | Deuterocanonical, Greek LXX, book + chapter:verse |

## License

MIT. The source texts are from public/open repositories:
- Hebrew OT: Westminster Leningrad Codex (via wjbaker2025/hebrew-holy-tanakh)
- Greek NT: SBL Greek New Testament (Faithlife/SBLGNT)
- Deuterocanonical: Swete's Septuagint (nathans/lxx-swete)

Used here for research and study.
