from __future__ import annotations

import argparse
import os
from pathlib import Path
import re
import urllib.error
import urllib.request

ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_TARGET_DIR = ROOT_DIR / "data" / "raw" / "snapshots"
PADRON_URL = "https://secihti.mx/padron-de-beneficiarios/"

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)


def log_status(message: str) -> None:
    print(f"[downloader] {message}", flush=True)


def fetch_page_html(url: str) -> str:
    log_status(f"Fetching page: {url}")
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            html = response.read().decode("utf-8")
            return html
    except Exception as exc:
        log_status(f"Error fetching page {url}: {exc}")
        raise


def extract_excel_links(html: str) -> list[str]:
    # Find all hrefs pointing to .xlsx or .xls files
    links = re.findall(r'href=["\'](https?://[^"\']+\.xlsx?)["\']', html, re.IGNORECASE)
    # Deduplicate
    unique_links = sorted(list(set(links)))
    return unique_links


def infer_year_from_url(url: str) -> int | None:
    # Look for year in path like /2024/ or in file name like _2024
    match_path = re.search(r"/((?:19|20)\d{2})/", url)
    if match_path:
        return int(match_path.group(1))

    match_name = re.search(r"((?:19|20)\d{2})", url)
    if match_name:
        return int(match_name.group(1))

    return None


def download_file(url: str, dest_path: Path, force: bool = False) -> bool:
    if dest_path.exists() and not force:
        log_status(f"Skipping (already exists): {dest_path.name}")
        return True

    log_status(f"Downloading {url} -> {dest_path}")
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            with open(dest_path, "wb") as out_file:
                # Read in chunks
                block_size = 8192
                while True:
                    buffer = response.read(block_size)
                    if not buffer:
                        break
                    out_file.write(buffer)
        log_status(f"Successfully downloaded: {dest_path.name}")
        return True
    except urllib.error.HTTPError as err:
        log_status(f"HTTP Error {err.code} for {url}: {err.reason}")
    except Exception as exc:
        log_status(f"Failed to download {url}: {exc}")
    return False


def run() -> None:
    parser = argparse.ArgumentParser(
        description="Descarga de archivos Excel de padrones de beneficiarios CONAHCYT/SECIHTI."
    )
    parser.add_argument(
        "--scope",
        choices=["all", "foreign", "national", "s190"],
        default="all",
        help="Filtrar archivos a descargar por alcance (todos, extranjero, nacionales, o mixtos S190)",
    )
    parser.add_argument(
        "--year",
        type=int,
        help="Descargar archivos únicamente para un año específico (ej. 2024)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Forzar la descarga e ignorar archivos ya existentes",
    )
    args = parser.parse_args()

    html = fetch_page_html(PADRON_URL)
    links = extract_excel_links(html)
    log_status(f"Discovered {len(links)} Excel file link(s)")

    download_count = 0
    skipped_count = 0

    for link in links:
        filename = link.split("/")[-1]
        year = infer_year_from_url(link)

        # Filter by year if specified
        if args.year and year != args.year:
            continue

        if not year:
            log_status(f"Could not infer year for {filename}, skipping.")
            continue

        # Filter by scope
        lowered_name = filename.lower()
        is_foreign = any(kw in lowered_name for kw in ["extranj", "foreign", "abroad", "bext"])
        
        # We only want core national scholarships (e.g. 'Becas_Nacionales_...xlsx')
        # We exclude postdocs, sabbaticals, and repatriations
        is_excluded_type = any(kw in lowered_name for kw in ["posdoc", "sabatic", "repatriac"])
        is_national = (any(kw in lowered_name for kw in ["nacional", "bnac"]) and not is_excluded_type)
        is_s190 = "s190" in lowered_name

        if args.scope == "foreign" and not is_foreign and not is_s190:
            continue
        elif args.scope == "national" and not is_national and not is_s190:
            continue
        elif args.scope == "s190" and not is_s190:
            continue

        dest_path = DEFAULT_TARGET_DIR / str(year) / filename
        success = download_file(link, dest_path, force=args.force)
        if success:
            download_count += 1
        else:
            skipped_count += 1

    log_status(f"Finished: {download_count} file(s) downloaded, {skipped_count} skipped/failed.")


if __name__ == "__main__":
    run()
