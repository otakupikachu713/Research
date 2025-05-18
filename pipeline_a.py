# pipeline_a.py
import json, pathlib, subprocess, sys

# Path to the james parser in the same folder as this script
PARSER = pathlib.Path(__file__).parent / "james.py"
OUT_DIR = pathlib.Path(__file__).parent / "james_output"

OUT_DIR.mkdir(parents=True, exist_ok=True)

def _ensure_ran(pdf_path: pathlib.Path):
    """Run james.py once per PDF if output JSON not present."""
    # Output JSON filename: <stem>_layout.json
    out_json = OUT_DIR / f"{pdf_path.stem}_layout.json"
    if out_json.exists():
        return out_json
    # Invoke james.py with --pdf and --output flags
    cmd = [sys.executable,
           str(PARSER),
           "--pdf", str(pdf_path),
           "--output", str(out_json)]
    subprocess.run(cmd, check=True)
    return out_json


def run_pipeline_a(pdf_path: str):
    pdf_path = pathlib.Path(pdf_path)
    out_json = _ensure_ran(pdf_path)
    return json.loads(out_json.read_text())
