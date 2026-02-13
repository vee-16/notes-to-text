from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List

import requests
from dotenv import load_dotenv

BASE = "https://www.handwritingocr.com/api/v3"


def req(method: str, url: str, token: str, **kw) -> requests.Response:
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    for _ in range(8):
        r = requests.request(method, url, headers=headers, timeout=60, **kw)
        if r.status_code != 429:
            return r
        time.sleep(float(r.headers.get("Retry-After", "1")))
    return r


def upload(pdf: Path, token: str) -> str:
    with pdf.open("rb") as f:
        r = req(
            "POST",
            f"{BASE}/documents",
            token,
            files={"file": (pdf.name, f)},
            data={"action": "transcribe"},
        )
    
    if r.status_code in (401, 403):
        raise RuntimeError(f"Upload failed ({r.status_code}): {r.text}")
    r.raise_for_status()
    return r.json()["id"]


def wait_processed(doc_id: str, token: str, poll_s: float = 1.0) -> Dict[str, Any]:
    url = f"{BASE}/documents/{doc_id}"
    while True:
        r = req("GET", url, token)
        if r.status_code == 202:
            time.sleep(poll_s)
            continue
        r.raise_for_status()
        j = r.json()
        if j.get("status") == "processed":
            return j
        time.sleep(poll_s)


def extract_pages(data: Dict[str, Any]) -> Dict[int, str]:
    return {
        int(r["page_number"]): (r.get("transcript") or "")
        for r in data.get("results", [])
        if "page_number" in r
    }


def save_outputs(pdf: Path, out_base: Path, data: Dict[str, Any]) -> Path:
    doc_out = out_base / pdf.stem
    doc_out.mkdir(parents=True, exist_ok=True)

    stem = pdf.stem
    (doc_out / f"{stem}.raw.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), "utf-8")

    pages = extract_pages(data)
    (doc_out / f"{stem}.pages.json").write_text(json.dumps(pages, ensure_ascii=False, indent=2), "utf-8")

    merged = "\n\n".join(pages[p].rstrip() for p in sorted(pages)).rstrip() + "\n"
    (doc_out / f"{stem}.txt").write_text(merged, "utf-8")

    return doc_out


def iter_pdfs(dir_path: Path) -> List[Path]:
    return sorted(p for p in dir_path.glob("*.pdf") if p.is_file())


def process_one(pdf: Path, out_base: Path, token: str) -> None:
    print(f"\nUploading: {pdf.name}")
    doc_id = upload(pdf, token)
    print(f"Document id: {doc_id}")

    data = wait_processed(doc_id, token, poll_s=1.0)

    out_dir = save_outputs(pdf, out_base, data)
    pages = extract_pages(data)

    print(f"Saved to {out_dir}")
    print(f"page_count={data.get('page_count')} results={len(pages)}")


def usage() -> str:
    return (
        "Usage:\n"
        "  Single PDF:\n"
        "    python notes_to_text_extraction.py --pdf ./data/{file-name}.pdf --out ./out\n"
        "  Batch (all PDFs in a folder):\n"
        "    python notes_to_text_extraction.py --dir ./data --out ./out\n"
    )


def main(argv: List[str]) -> None:
    load_dotenv()
    token = (os.getenv("HANDWRITING_OCR_TOKEN") or "").strip()
    if not token:
        raise SystemExit("Missing HANDWRITING_OCR_TOKEN (put it in .env)")

    if "--out" not in argv:
        raise SystemExit(usage())

    out_base = Path(argv[argv.index("--out") + 1]).expanduser().resolve()
    out_base.mkdir(parents=True, exist_ok=True)

    if "--pdf" in argv:
        pdf = Path(argv[argv.index("--pdf") + 1]).expanduser().resolve()
        process_one(pdf, out_base, token)
        return

    if "--dir" in argv:
        d = Path(argv[argv.index("--dir") + 1]).expanduser().resolve()
        pdfs = iter_pdfs(d)
        if not pdfs:
            raise SystemExit(f"No PDFs found in: {d}")
        print(f"Found {len(pdfs)} PDF(s) in {d}")
        for pdf in pdfs:
            process_one(pdf, out_base, token)
        return

    raise SystemExit(usage())


if __name__ == "__main__":
    import sys
    main(sys.argv[1:])