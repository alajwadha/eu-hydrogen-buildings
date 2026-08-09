"""
01_download.py — Country-parameterised EUBUCCO download
================================================================================

PURPOSE
-------
Pull the EUBUCCO v0.2 building-stock dataset for a single country, identified
by its 2-letter ISO code via `--country`. The country's NUTS2 partition list
is read from `code/data/country_config/{cc}.yaml`; each partition becomes
one S3 download.

CONFIG
------
Every country has a YAML file under `code/data/country_config/`. The
`eubucco.nuts2_partitions` list drives this script. For Luxembourg the list
is `[LU00]` (single partition); for France it is the 22 FRxx codes.

DATASET
-------
EUBUCCO v0.2
  URL base:  s3://eubucco/v0.2/buildings/parquet/nuts_id={NUTS2}/{NUTS2}.parquet
  Access:    anonymous S3 (no registration)
  Format:    GeoParquet, CRS EPSG:3035 (ETRS89 / LAEA)
  Attributes (per building): footprint geometry, height (~73% coverage in
             v0.1, higher in v0.2), type (residential / non-res),
             construction year (~24% in v0.1, country-dependent).
  License:   ODbL v1.0 (Open Database License — commercial use OK with
             attribution and share-alike).
  Citation:  Milojevic-Dupont N. et al. (2023). EUBUCCO v0.1: European
             building stock characteristics in a common and open database
             for 200+ million individual buildings. Scientific Data 10:147.
             DOI 10.1038/s41597-023-02040-2. v0.2 data via eubucco.com.

NOTE ON GBA (HISTORICAL)
------------------------
Earlier iterations of this pipeline also downloaded the GBA.ODbLPolygon tile
(Zhu et al. 2025, DOI 10.14459/2025mp1782307) for cross-validation. The
GBA cross-check found GBA's residential floor area to be ~1.4x EUBUCCO's,
consistent with GBA's looser polygon definition that includes sheds,
extensions, and garages. That result is preserved in the paper's
methodology section as a one-time published finding (Zhu2025 remains in
the bibliography). GBA is no longer pulled at pipeline runtime because:

  1. The 10 GB tile took ~22 minutes to bbox-filter through Drive FUSE
     in Colab, dominating total pipeline time.
  2. The TUM-hosted WFS endpoint (which would have allowed bbox-only
     fetches) has a server-side response-size cap of ~1 MB, requiring
     thousands of paged requests to retrieve LU — no net speed gain.
  3. The cross-check ratio is a stable, published value; re-deriving it
     on every Colab run is not worth the cost.

If a fresh cross-check is needed (e.g., new EUBUCCO version), the
pre-removal git history contains a working load_gba() implementation
in commit d248600 (code/scripts/luxembourg/02_classify.py).

INTENDED OUTPUTS
----------------
  code/data/raw/eubucco/{NUTS2}.parquet                  (one per partition)
  code/data/raw/{country_code}_provenance.txt            (URLs, MD5s, citation)

USAGE
-----
    python code/scripts/country_build/01_download.py --country LU
    python code/scripts/country_build/01_download.py --country FR
    python code/scripts/country_build/01_download.py --country LU --skip-eubucco
    python code/scripts/country_build/01_download.py --country LU --force

IDEMPOTENCY
-----------
If the destination file already exists, the download is skipped unless
`--force` is passed. This makes the script safe to re-run after an
interrupted session — only missing files are fetched.

REPRODUCIBILITY ARTEFACT
------------------------
After each run, `{cc}_provenance.txt` is written with:
  - dataset name and version, for each NUTS2 partition
  - exact URL fetched
  - destination path
  - download status (OK / FAILED)
  - MD5 of the downloaded file (for byte-for-byte reproducibility)
  - license string
  - citation
This file is committed to the repository so the methods section of the paper
can cite "downloaded on YYYY-MM-DD via 01_download.py, MD5 abc123…".

NETWORKING
----------
Uses `requests` (preferred — handles HuggingFace LFS redirects + retries) with
`urllib` fallback for environments where requests isn't installed.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import sys
import time
import urllib.request
from pathlib import Path
from urllib.error import URLError


# ── Paths ───────────────────────────────────────────────────────────────────
# Banner: set the environment variable `EUHB_RAW_DIR` to override the default
# raw-data location. This is used by the Colab notebook to redirect downloads
# to Google Drive (MyDrive/eu-hydrogen-raw/), keeping the laptop out of the
# I/O path. Default behaviour (laptop / Codespaces) is unchanged.
REPO_ROOT = Path(__file__).resolve().parents[3]
RAW_DIR = Path(
    os.environ.get("EUHB_RAW_DIR", REPO_ROOT / "code" / "data" / "raw")
)
EUBUCCO_DIR = RAW_DIR / "eubucco"

# Import country config loader (relative to repo)
sys.path.insert(0, str(REPO_ROOT / "code" / "src"))
from CountryConfig import load_country_config  # noqa: E402


# ── Download helpers ────────────────────────────────────────────────────────
def stream_download(url: str, dest: Path, label: str, force: bool = False,
                    chunk_mb: int = 8) -> bool:
    """Stream a URL to a destination file with progress reporting.

    Prefers the `requests` library (more robust with HF redirects + retries),
    falls back to stdlib urllib.
    """
    if dest.exists() and not force:
        size_mb = dest.stat().st_size / 1024 / 1024
        print(f"[{label}] already present at {dest} ({size_mb:.1f} MB) — skipping")
        print(f"          pass --force to re-download")
        return True

    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".part")

    print(f"[{label}] downloading: {url}")
    print(f"          to:          {dest}")

    chunk = chunk_mb * 1024 * 1024
    start = time.time()

    # Path 1: requests (preferred — handles HuggingFace LFS redirects)
    try:
        import requests
        try:
            with requests.get(url, stream=True, allow_redirects=True,
                              timeout=(15, 300),
                              headers={"User-Agent": "eu-hydrogen-buildings/0.1"}) as r:
                if r.status_code != 200:
                    print(f"[{label}] FAILED with HTTP {r.status_code}: {r.reason}")
                    return False
                total = r.headers.get("Content-Length")
                total = int(total) if total else None
                done = 0
                with open(tmp, "wb") as f:
                    for buf in r.iter_content(chunk_size=chunk):
                        if not buf:
                            continue
                        f.write(buf)
                        done += len(buf)
                        elapsed = max(time.time() - start, 0.001)
                        rate = done / 1024 / 1024 / elapsed
                        if total:
                            pct = done * 100 / total
                            print(f"[{label}]   {done/1024/1024:6.1f} / "
                                  f"{total/1024/1024:6.1f} MB ({pct:4.1f}%) "
                                  f"@ {rate:5.1f} MB/s", end="\r")
                        else:
                            print(f"[{label}]   {done/1024/1024:6.1f} MB "
                                  f"downloaded @ {rate:5.1f} MB/s", end="\r")
            print()
            tmp.rename(dest)
            size_mb = dest.stat().st_size / 1024 / 1024
            print(f"[{label}] done — {size_mb:.1f} MB saved to {dest}")
            return True
        except requests.RequestException as e:
            if tmp.exists():
                tmp.unlink()
            print(f"[{label}] FAILED (requests): {type(e).__name__}: {e}")
            return False
    except ImportError:
        pass  # fall through to urllib

    # Path 2: urllib fallback (simpler, less robust)
    try:
        req = urllib.request.Request(
            url, headers={"User-Agent": "eu-hydrogen-buildings/0.1"})
        with urllib.request.urlopen(req, timeout=300) as resp, open(tmp, "wb") as f:
            total = resp.headers.get("Content-Length")
            total = int(total) if total else None
            done = 0
            while True:
                buf = resp.read(chunk)
                if not buf:
                    break
                f.write(buf)
                done += len(buf)
                elapsed = max(time.time() - start, 0.001)
                rate = done / 1024 / 1024 / elapsed
                if total:
                    pct = done * 100 / total
                    print(f"[{label}]   {done/1024/1024:6.1f} / "
                          f"{total/1024/1024:6.1f} MB ({pct:4.1f}%) "
                          f"@ {rate:5.1f} MB/s", end="\r")
                else:
                    print(f"[{label}]   {done/1024/1024:6.1f} MB "
                          f"downloaded @ {rate:5.1f} MB/s", end="\r")
        print()
        tmp.rename(dest)
        size_mb = dest.stat().st_size / 1024 / 1024
        print(f"[{label}] done — {size_mb:.1f} MB saved to {dest}")
        return True
    except (URLError, TimeoutError, OSError) as e:
        if tmp.exists():
            tmp.unlink()
        print(f"[{label}] FAILED (urllib): {type(e).__name__}: {e}")
        return False


def md5_check(path: Path, label: str) -> str:
    """Return the MD5 of a file (for reproducibility logging).

    Skips silently with an explanatory message if:
      - The file is large (>1 GB) AND lives on a fuse-mounted Drive — Google
        Drive's FUSE mount intermittently returns ``OSError [Errno 107]
        Transport endpoint is not connected`` when chunk-reading huge files,
        which has nothing to do with the file's integrity and shouldn't crash
        the download step.
      - Any other ``OSError`` occurs mid-read (mount drops, transient I/O).

    Returns the MD5 hex string on success, or one of:
      - "skipped:too-large-on-drive"
      - "skipped:io-error"
    The provenance log records whichever string we return.
    """
    try:
        size_mb = path.stat().st_size / 1024 / 1024
    except OSError as e:
        print(f"[{label}] MD5 skipped - cannot stat file: {e}")
        return "skipped:io-error"

    # Files >1 GB on a Drive mount: skip rather than risk a transport-endpoint
    # crash. The download itself already streamed the bytes, so corruption at
    # rest is unlikely; the URL + size in the provenance log is enough.
    on_drive = "/content/drive/" in str(path) or "/drive/MyDrive/" in str(path)
    if on_drive and size_mb > 1024:
        print(f"[{label}] MD5 skipped - file is {size_mb:.0f} MB on Drive mount")
        print(f"          (Drive FUSE can choke on chunked reads of >1 GB files)")
        return "skipped:too-large-on-drive"

    h = hashlib.md5()
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
    except OSError as e:
        print(f"[{label}] MD5 skipped - I/O error mid-read: {type(e).__name__}: {e}")
        return "skipped:io-error"
    digest = h.hexdigest()
    print(f"[{label}] MD5: {digest}")
    return digest


def write_provenance(records: list[dict], country_code: str,
                     country_name: str) -> None:
    """Write a provenance log next to the downloads for reproducibility."""
    log = RAW_DIR / f"{country_code.lower()}_provenance.txt"
    with open(log, "w") as f:
        f.write(f"EUBUCCO download — {country_name}\n")
        f.write(f"Run at: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}\n")
        f.write("=" * 60 + "\n\n")
        for r in records:
            for k, v in r.items():
                f.write(f"  {k}: {v}\n")
            f.write("\n")
    print(f"\nProvenance log written to {log}")


def _safe_rel(p: Path) -> str:
    """Render a path relative to REPO_ROOT if possible, otherwise absolute.

    `pathlib.Path.relative_to` raises ValueError when the target is not under
    the base. When `EUHB_RAW_DIR` redirects raw I/O outside the repo (e.g. to
    Google Drive in the Colab notebook), we just log the absolute path.
    """
    try:
        return str(p.relative_to(REPO_ROOT))
    except ValueError:
        return str(p)


# ── Main ────────────────────────────────────────────────────────────────────
def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--country", required=True,
                        help="2-letter ISO country code (e.g. LU, FR, DE)")
    parser.add_argument("--skip-eubucco", action="store_true",
                        help="Skip EUBUCCO download")
    parser.add_argument("--force", action="store_true",
                        help="Re-download even if destination exists")
    args = parser.parse_args()

    cfg = load_country_config(args.country)

    print("=" * 60)
    print(f"{cfg.country_name} ({cfg.country_code}) — EUBUCCO download")
    print("=" * 60)
    print(f"Repo root: {REPO_ROOT}")
    print(f"Output:    {RAW_DIR}")
    print(f"Partitions: {cfg.nuts2_partitions}")
    print()

    EUBUCCO_DIR.mkdir(parents=True, exist_ok=True)

    records: list[dict] = []

    if not args.skip_eubucco:
        for nuts2 in cfg.nuts2_partitions:
            url = cfg.eubucco_url(nuts2)
            dest = EUBUCCO_DIR / cfg.eubucco_filename(nuts2)
            ok = stream_download(url, dest, label=f"EUBUCCO {nuts2}",
                                 force=args.force)
            records.append({
                "dataset": f"EUBUCCO v0.2 NUTS2={nuts2}",
                "url": url,
                "dest": _safe_rel(dest),
                "status": "OK" if ok else "FAILED",
                "md5": md5_check(dest, f"EUBUCCO {nuts2}") if ok else "N/A",
                "license": cfg.eubucco_license,
                "citation": ("Milojevic-Dupont N. et al. (2023). EUBUCCO v0.1. "
                             "Scientific Data 10:147. DOI 10.1038/s41597-023-02040-2. "
                             "v0.2 data: https://eubucco.com/files/v0.2"),
            })

    if records:
        write_provenance(records, cfg.country_code, cfg.country_name)

    print()
    print("=" * 60)
    failed = [r for r in records if r["status"] == "FAILED"]
    if failed:
        print(f"{len(failed)} download(s) failed.")
        for r in failed:
            print(f"  — {r['dataset']}: {r['url']}")
        print("\nIf transient: retry. If persistent: check the URLs in script 01")
        print("are still valid — datasets can be moved/renamed.")
        return 1
    print(f"All {len(records)} downloads complete. Next step:")
    print(f"    python code/scripts/country_build/02_classify.py "
          f"--country {cfg.country_code}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
