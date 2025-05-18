# pipeline_b.py
import json, pathlib, subprocess, sys

# Path to the haonan1 parser in the same folder as this script
PARSER = pathlib.Path(__file__).parent / "haonan1.py"
OUT_ROOT = pathlib.Path(__file__).parent / "output_pdfs"

def _ensure_ran(pdf_path: pathlib.Path):
    folder = OUT_ROOT / pdf_path.stem
    out_json = folder / f"{pdf_path.stem}.json"
    if out_json.exists():
        return out_json
    folder.mkdir(parents=True, exist_ok=True)
    cmd = [sys.executable, str(PARSER),
           "--pdf", str(pdf_path),
           "--out_dir", str(folder)]
    subprocess.run(cmd, check=True)
    return out_json


def run_pipeline_b(pdf_path: str):
    pdf_path = pathlib.Path(pdf_path)
    out_json = _ensure_ran(pdf_path)
    return json.loads(out_json.read_text())
