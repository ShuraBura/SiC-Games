---
name: Sci-Hub Paper Downloader
description: Download paywalled academic papers from Sci-Hub by DOI using stealth Playwright browser automation. Use when the user provides DOI strings to download, asks to "grab papers", "download PDFs by DOI", or wants to fetch paywalled papers.
disable-model-invocation: false
argument-hint: "[doi ...] or [doi:filename.pdf ...]"
allowed-tools: Bash Read
shell: powershell
---

Download academic papers from Sci-Hub by DOI using the stealth Playwright downloader.

## Arguments

`$ARGUMENTS` — one or more DOIs, space-separated. Two formats accepted:

- Plain DOI: `10.1002/evan.20046` — filename auto-generated from page title
- DOI with name: `10.1002/evan.20046:Marlowe2005.pdf` — saved with that exact name

Optional flags (pass anywhere in arguments):
- `--dest <path>` — override output directory (default: `G:\My Drive\docs\SiC Games Docs\lit`)
- `--prefix <str>` — override filename prefix (default: `SiC_Games_`)
- `--no-prefix` — disable prefix entirely

## Steps

1. Check that `$ARGUMENTS` is not empty. If empty, print usage and stop.
2. Run the downloader:
   ```powershell
   python "${CLAUDE_SKILL_DIR}/scripts/scihub_download.py" $ARGUMENTS
   ```
3. A visible Chromium window opens, passes the DDoS-Guard challenge, and downloads each paper.
4. After the script exits, report the results: filenames saved, sizes, and any failures.
5. If a DOI failed ("NO PDF"), note it — Sci-Hub may not have that paper.

## Supporting files

- `scripts/scihub_download.py` — Playwright stealth downloader (the engine)
