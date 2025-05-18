#!/usr/bin/env python3
"""
combine_artifacts_with_gui.py

Adds a simple Tkinter GUI allowing users to select which PDFs to merge,
and then merges the corresponding PDF, image, and JSON files.

The input/output directory configuration remains unchanged.
"""
import os
import json
import time
import warnings
from pathlib import Path
from PIL import Image
import logging
from PyPDF2 import PdfMerger
from PyPDF2.errors import PdfReadWarning
import tkinter as tk
from tkinter import filedialog, messagebox

# ---------------------- CONFIGURATION ----------------------
PDF_INPUT_DIR   = Path("./small_dataset/test/pdfs")
IMG_INPUT_DIR   = Path("./small_dataset/test/images")
JSON_INPUT_DIR  = Path("./small_dataset/test/annotations")
OUTPUT_BASE_DIR = Path("./combined_outputs")  # will contain subfolders: pdfs, images, jsons
# -----------------------------------------------------------

warnings.filterwarnings("ignore", category=PdfReadWarning)
logging.getLogger("PyPDF2").setLevel(logging.ERROR)


def select_pdfs():
    """Open a file dialog to select one or more PDF files to merge."""
    root = tk.Tk()
    root.withdraw()
    files = filedialog.askopenfilenames(
        title="Select PDF files to merge",
        initialdir=str(PDF_INPUT_DIR.resolve()),
        filetypes=[("PDF files", "*.pdf")]
    )
    if not files:
        messagebox.showinfo("No Selection", "No PDF files selected. Exiting.")
        exit(0)
    return [Path(f) for f in files]


def merge_pdfs(pdf_paths, output_pdf, metrics):
    start = time.perf_counter()
    merger = PdfMerger()
    for pdf in pdf_paths:
        merger.append(str(pdf))
    merger.write(str(output_pdf))
    merger.close()
    elapsed = time.perf_counter() - start
    metrics['pdf'] = {
        'file_count': len(pdf_paths),
        'duration_sec': elapsed
    }
    print(f"[PDF] Merged {len(pdf_paths)} files in {elapsed:.2f}s → {output_pdf}")


def merge_images_for_pdfs(pdf_paths, img_dir, output_pdf, metrics):
    stems = [p.stem for p in pdf_paths]
    img_paths = []
    for stem in stems:
        # find any matching image by stem
        matches = list(img_dir.glob(f"{stem}.*"))
        img_paths.extend(matches)
    img_paths = sorted([p for p in img_paths if p.suffix.lower() in {'.png', '.jpg', '.jpeg', '.tiff'}])
    if not img_paths:
        print("[IMG] No images found for selected PDFs.")
        metrics['images'] = {'file_count': 0, 'duration_sec': 0.0}
        return
    start = time.perf_counter()
    imgs = []
    for p in img_paths:
        im = Image.open(p)
        if im.mode in ('RGBA','LA'):
            im = im.convert('RGB')
        imgs.append(im)
    imgs[0].save(
        str(output_pdf),
        save_all=True,
        append_images=imgs[1:]
    )
    elapsed = time.perf_counter() - start
    metrics['images'] = {
        'file_count': len(img_paths),
        'duration_sec': elapsed
    }
    print(f"[IMG] Merged {len(img_paths)} files in {elapsed:.2f}s → {output_pdf}")


def combine_jsons_for_pdfs(pdf_paths, json_dir, output_json, metrics):
    stems = [p.stem for p in pdf_paths]
    json_paths = []
    for stem in stems:
        path = json_dir / f"{stem}.json"
        if path.exists():
            json_paths.append(path)
    start = time.perf_counter()
    combined = []
    for jf in json_paths:
        with open(jf, 'r', encoding='utf-8') as f:
            combined.append(json.load(f))
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(combined, f, indent=2)
    elapsed = time.perf_counter() - start
    metrics['json'] = {
        'file_count': len(json_paths),
        'duration_sec': elapsed
    }
    print(f"[JSON] Merged {len(json_paths)} files in {elapsed:.2f}s → {output_json}")


def save_metrics(metrics, output_path: Path):
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(metrics, f, indent=2)
    print(f"[METRICS] Saved metrics → {output_path}")


def main():
    selected_pdfs = select_pdfs()

    pdf_out_dir   = OUTPUT_BASE_DIR / "pdfs"
    img_out_dir   = OUTPUT_BASE_DIR / "images"
    json_out_dir  = OUTPUT_BASE_DIR / "jsons"
    for d in (pdf_out_dir, img_out_dir, json_out_dir):
        d.mkdir(parents=True, exist_ok=True)

    metrics = {'run_start': time.strftime('%Y-%m-%dT%H:%M:%S')}

    merge_pdfs(selected_pdfs, pdf_out_dir / 'selected_pdfs_merged.pdf', metrics)
    merge_images_for_pdfs(selected_pdfs, IMG_INPUT_DIR, img_out_dir / 'selected_images_merged.pdf', metrics)
    combine_jsons_for_pdfs(selected_pdfs, JSON_INPUT_DIR, json_out_dir / 'all_jsons_combined.json', metrics)

    metrics['run_end'] = time.strftime('%Y-%m-%dT%H:%M:%S')
    save_metrics(metrics, OUTPUT_BASE_DIR / 'performance_metrics.json')

if __name__ == '__main__':
    main()
