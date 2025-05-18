import sys, pathlib, json
from pipeline_a import run_pipeline_a
from pipeline_b import run_pipeline_b

BASE = pathlib.Path("base_dataset/train")
PDFS = BASE / "pdfs"
IMGS = BASE / "images"

OUT_A = pathlib.Path("out_pipelineA")
OUT_B = pathlib.Path("out_pipelineB")
for d in (OUT_A / "pdfs", OUT_A / "images", OUT_B / "pdfs", OUT_B / "images"):
    d.mkdir(parents=True, exist_ok=True)

for folder, runner, root in [
    (PDFS, run_pipeline_a, OUT_A / "pdfs"),
    (IMGS, run_pipeline_a, OUT_A / "images"),
    (PDFS, run_pipeline_b, OUT_B / "pdfs"),
    (IMGS, run_pipeline_b, OUT_B / "images"),
]:
    for f in folder.glob("*"):
        try:
            result = runner(str(f))
            out_file = root / f"{f.stem}.json"
            with open(out_file, "w") as fp:
                json.dump(result, fp, indent=2)
        except Exception as e:
            print(f"Error {f.name}: {e}", file=sys.stderr)

print("Completed: outputs in out_pipelineA/ and out_pipelineB/.")
