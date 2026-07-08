"""
Sci-Hub stealth downloader using Playwright.

Usage:
  python scihub_download.py [--dest DIR] [--prefix STR] [--no-prefix] doi [doi ...]

DOI formats:
  10.1002/evan.20046              -> auto-generated filename from page title
  10.1002/evan.20046:custom.pdf  -> saved as <prefix>custom.pdf
"""

import argparse, asyncio, os, re, sys, urllib.request
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

BASE = "https://sci-hub.ru"
DEFAULT_DEST = r"G:\My Drive\docs\SiC Games Docs\lit"
DEFAULT_PREFIX = "SiC_Games_"


def extract_pdf_url(html: str) -> str | None:
    patterns = [
        r'src=["\']([^"\']*\.pdf(?:\?[^"\']*)?)["\']',
        r'href=["\']([^"\']*\.pdf(?:\?[^"\']*)?)["\']',
        r'src=([^\s"\'<>]+\.pdf)',
    ]
    for pat in patterns:
        m = re.search(pat, html, re.IGNORECASE)
        if m:
            url = m.group(1)
            if url.startswith("//"):
                return "https:" + url
            if url.startswith("/"):
                return BASE + url
            if url.startswith("http"):
                return url
    return None


def extract_title(html: str) -> str | None:
    m = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
    if not m:
        return None
    raw = m.group(1)
    raw = re.sub(r"\s*[-|]\s*Sci.?Hub.*", "", raw, flags=re.IGNORECASE).strip()
    safe = re.sub(r"[^\w\s-]", "", raw).strip()
    safe = re.sub(r"\s+", "_", safe)[:60]
    return safe if safe and safe.lower() not in ("sci_hub", "") else None


def doi_to_safe(doi: str) -> str:
    return re.sub(r"[^\w.-]", "_", doi)[:80]


async def download_one(page, doi: str, out_path: str) -> bool:
    url = f"{BASE}/{doi}"
    print(f"\n  -> {doi}", flush=True)
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=30_000)
        await page.wait_for_timeout(6_000)

        html = await page.content()
        pdf_url = extract_pdf_url(html)

        if not pdf_url:
            print(f"     NO PDF (page title: {await page.title()!r})", flush=True)
            return False

        # Resolve auto filename
        if out_path.endswith("__AUTO__"):
            slug = extract_title(html) or doi_to_safe(doi)
            out_path = out_path[: -len("__AUTO__")] + slug + ".pdf"

        # Avoid overwriting existing good files
        if os.path.exists(out_path) and os.path.getsize(out_path) > 10_000:
            print(f"     SKIP already exists: {os.path.basename(out_path)}", flush=True)
            return True

        cookies = await page.context.cookies()
        cookie_header = "; ".join(f"{c['name']}={c['value']}" for c in cookies)

        req = urllib.request.Request(pdf_url)
        req.add_header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120")
        req.add_header("Referer", url)
        if cookie_header:
            req.add_header("Cookie", cookie_header)

        with urllib.request.urlopen(req, timeout=60) as resp:
            data = resp.read()

        with open(out_path, "wb") as f:
            f.write(data)

        print(f"     OK  {os.path.basename(out_path)}  ({len(data)//1024} KB)", flush=True)
        return True

    except Exception as exc:
        print(f"     FAIL  {exc}", flush=True)
        return False


async def main(cfg) -> None:
    papers: list[tuple[str, str]] = []
    for tok in cfg.dois:
        if ":" in tok and not tok.startswith("http"):
            doi, fname = tok.split(":", 1)
            out = os.path.join(cfg.dest, cfg.prefix + fname)
        else:
            out = os.path.join(cfg.dest, cfg.prefix + "__AUTO__")
            doi = tok
        papers.append((doi, out))

    os.makedirs(cfg.dest, exist_ok=True)
    results: dict[str, str] = {}

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 800},
        )
        page = await context.new_page()
        await Stealth().apply_stealth_async(page)

        print("Priming Sci-Hub session...", flush=True)
        await page.goto(BASE, wait_until="domcontentloaded", timeout=30_000)
        await page.wait_for_timeout(8_000)
        title = await page.title()
        print(f"  Page: {title!r}", flush=True)
        if "ddos" in title.lower():
            print("  Still on challenge — waiting 10 s more...", flush=True)
            await page.wait_for_timeout(10_000)
            print(f"  Page: {await page.title()!r}", flush=True)

        for doi, out_path in papers:
            ok = await download_one(page, doi, out_path)
            results[doi] = "ok" if ok else "failed"
            await page.wait_for_timeout(2_000)

        await browser.close()

    print("\n=== Results ===")
    for doi, status in results.items():
        print(f"  {status:8s}  {doi}")


if __name__ == "__main__":
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(
        description="Download papers from Sci-Hub via stealth Playwright"
    )
    parser.add_argument(
        "dois",
        nargs="+",
        metavar="doi[:filename.pdf]",
        help="DOIs to download. Append :name.pdf to override filename.",
    )
    parser.add_argument(
        "--dest",
        default=DEFAULT_DEST,
        help=f"Output directory (default: {DEFAULT_DEST})",
    )
    parser.add_argument(
        "--prefix",
        default=DEFAULT_PREFIX,
        help=f"Filename prefix (default: {DEFAULT_PREFIX!r})",
    )
    parser.add_argument(
        "--no-prefix",
        action="store_true",
        help="Disable filename prefix",
    )

    cfg = parser.parse_args()
    if cfg.no_prefix:
        cfg.prefix = ""

    asyncio.run(main(cfg))
