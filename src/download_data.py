"""Download the JogjaPulse dataset from Zenodo and verify MD5 checksums."""
import hashlib
import time
from pathlib import Path
from urllib.error import ContentTooShortError, URLError
from urllib.request import urlretrieve

from config import RAW_JP

MAX_TRIES = 5
RECORD = "https://zenodo.org/records/23157460/files/{name}?download=1"
OUT_DIR = RAW_JP

FILES = {
    "presence_cell500m_daily.csv": "0b4d544e8c9ab26d69360821e9ebff27",
    "presence_kapanewon_hourly.csv": "90a4a8ae6eb68abc68f7a1021a51cce8",
    "od_home_visits_kapanewon_monthly.csv": "5857291c608dd5335f6d8833c1ec7b7a",
    "od_origin_homes_monthly.csv": "d14368c48d3937c9146ed9054aee3c79",
    "od_summary.csv": "139962d1c8101eb6873be6f902320efb",
    "home_maids_vs_population_kapanewon.csv": "0f01f7a3bb7027174cc1b5e1ad0e8224",
    "validation_night_presence_kapanewon.csv": "4a8d0f393fd6d4fa17fb0e60c6f7408e",
    "tier1_summary.csv": "d391339521ce3714f1616c430512b0e0",
    "README.md": "ac30f40e0e021cb2b131d529d782c75b",
}


def md5(path: Path) -> str:
    h = hashlib.md5()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, expected in FILES.items():
        dest = OUT_DIR / name
        if dest.exists() and md5(dest) == expected:
            print(f"ok (cached)  {name}")
            continue
        for attempt in range(1, MAX_TRIES + 1):
            print(f"downloading  {name} (attempt {attempt}) ...")
            try:
                urlretrieve(RECORD.format(name=name), dest)
            except (ContentTooShortError, URLError, OSError) as e:
                print(f"  failed: {e}")
                time.sleep(3 * attempt)
                continue
            if md5(dest) == expected:
                print(f"ok           {name}")
                break
            print("  MD5 mismatch, retrying")
        else:
            raise SystemExit(f"Could not download {name} after {MAX_TRIES} attempts")


if __name__ == "__main__":
    main()
