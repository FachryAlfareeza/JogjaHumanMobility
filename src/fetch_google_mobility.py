"""Fetch Google COVID-19 Community Mobility Reports for Indonesia.

Only the Indonesia files (20XX_ID_Region_Mobility_Report.csv) are pulled out of
Google's 98 MB region zip, using HTTP range requests, so the whole zip is never
downloaded. The DIY rows are also saved as a small separate file.

Source: https://www.google.com/covid19/mobility/ (data frozen on 15 Oct 2022)
"""
import io
import zipfile
from pathlib import Path
from urllib.request import Request, urlopen

import pandas as pd

ZIP_URL = "https://www.gstatic.com/covid19/mobility/Region_Mobility_Report_CSVs.zip"
OUT_DIR = Path(__file__).resolve().parents[1] / "data" / "raw" / "external" / "google_mobility"
YEARS = ["2021", "2022"]  # JogjaPulse window: Dec 2021 - Apr 2022


class HttpRangeFile(io.RawIOBase):
    """Read-only, seekable file object backed by HTTP Range requests."""

    def __init__(self, url: str):
        self.url = url
        self.pos = 0
        with urlopen(Request(url, method="HEAD")) as r:
            self.size = int(r.headers["Content-Length"])

    def seekable(self):
        return True

    def readable(self):
        return True

    def tell(self):
        return self.pos

    def seek(self, offset, whence=io.SEEK_SET):
        base = {io.SEEK_SET: 0, io.SEEK_CUR: self.pos, io.SEEK_END: self.size}[whence]
        self.pos = base + offset
        return self.pos

    def readinto(self, b):
        if self.pos >= self.size or len(b) == 0:
            return 0
        end = min(self.pos + len(b), self.size) - 1
        req = Request(self.url, headers={"Range": f"bytes={self.pos}-{end}"})
        with urlopen(req) as r:
            data = r.read()
        b[: len(data)] = data
        self.pos += len(data)
        return len(data)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    remote = io.BufferedReader(HttpRangeFile(ZIP_URL), buffer_size=1 << 20)
    frames = []
    with zipfile.ZipFile(remote) as zf:
        for year in YEARS:
            name = f"{year}_ID_Region_Mobility_Report.csv"
            dest = OUT_DIR / name
            if not dest.exists():
                print(f"extracting {name} ...")
                dest.write_bytes(zf.read(name))
            frames.append(pd.read_csv(dest, parse_dates=["date"]))

    df = pd.concat(frames, ignore_index=True)
    diy = df[df["sub_region_1"].fillna("").str.contains("Yogyakarta", case=False)]
    diy.to_csv(OUT_DIR / "google_mobility_diy.csv", index=False)
    print(f"saved {len(diy)} DIY rows -> google_mobility_diy.csv")


if __name__ == "__main__":
    main()
