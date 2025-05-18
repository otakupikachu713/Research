# evaluate_pipelines.py

import os
import json
import csv

from pipeline_a import run_pipeline_a
from pipeline_b import run_pipeline_b
from content_metrics import compute_content_metrics
from structural_metrics import compute_structural_metrics
from coherence_metrics import compute_coherence_metrics
from runtime_profiler import profile_pipeline

def load_combined_gt(path: str):
    with open(path, "r", encoding="utf-8") as f:
        pages = json.load(f)
    if not isinstance(pages, list):
        raise ValueError("Expected a list of page dicts in combined GT")
    return pages

def evaluate_document(
    pdf_filename: str,
    pdf_dir: str,
    combined_gt: list,
    report_json_dir: str
):
    stem = os.path.splitext(pdf_filename)[0]
    pdf_path = os.path.join(pdf_dir, pdf_filename)

    # 1. Run both pipelines
    predA = run_pipeline_a(pdf_path)
    predB = run_pipeline_b(pdf_path)

    # 2. Wrap combined GT under "pages"
    gt = {"pages": combined_gt}

    # 3. Compute metrics
    content_A = compute_content_metrics(predA, gt)
    content_B = compute_content_metrics(predB, gt)

    struct_A = compute_structural_metrics(predA, gt)
    struct_B = compute_structural_metrics(predB, gt)

    coher_A = compute_coherence_metrics(predA, gt)
    coher_B = compute_coherence_metrics(predB, gt)

    runtime_A = profile_pipeline(run_pipeline_a, pdf_path)
    runtime_B = profile_pipeline(run_pipeline_b, pdf_path)

    # 4. Per-document report
    report = {
        "document": pdf_filename,
        "content_A": content_A,
        "content_B": content_B,
        "structure_A": struct_A,
        "structure_B": struct_B,
        "coherence_A": coher_A,
        "coherence_B": coher_B,
        "runtime_A": runtime_A,
        "runtime_B": runtime_B,
    }

    # 5. Write JSON
    out_path = os.path.join(report_json_dir, f"{stem}_report.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as jf:
        json.dump(report, jf, indent=2)

    return report

def evaluate_documents(
    docs: list,
    pdf_dir: str,
    combined_gt: list,
    report_json_dir: str,
    report_csv_path: str
):
    fieldnames = [
        "document",
        # content A
        "precision_A","recall_A","F1_A","BLEU-4_A","local_align_score_A",
        # content B
        "precision_B","recall_B","F1_B","BLEU-4_B","local_align_score_B",
        # structure A
        "headings_count_A","headings_percent_A","figures_count_A","tables_count_A",
        # structure B
        "headings_count_B","headings_percent_B","figures_count_B","tables_count_B",
        # coherence A
        "pct_chunks_end_at_sentence_A","pct_sentences_split_A",
        "mean_tokens_A","std_tokens_A","max_tokens_A",
        # coherence B
        "pct_chunks_end_at_sentence_B","pct_sentences_split_B",
        "mean_tokens_B","std_tokens_B","max_tokens_B",
        # runtime
        "time_per_page_A","pages_per_second_A",
        "time_per_page_B","pages_per_second_B",
    ]

    os.makedirs(os.path.dirname(report_csv_path), exist_ok=True)
    with open(report_csv_path, "w", newline="", encoding="utf-8") as csvf:
        writer = csv.DictWriter(csvf, fieldnames=fieldnames)
        writer.writeheader()

        for doc in docs:
            rpt = evaluate_document(doc, pdf_dir, combined_gt, report_json_dir)
            row = {
                "document": rpt["document"],

                # content A
                "precision_A":         rpt["content_A"]["precision"],
                "recall_A":            rpt["content_A"]["recall"],
                "F1_A":                rpt["content_A"]["F1"],
                "BLEU-4_A":            rpt["content_A"]["BLEU-4"],
                "local_align_score_A": rpt["content_A"]["local_align_score"],

                # content B
                "precision_B":         rpt["content_B"]["precision"],
                "recall_B":            rpt["content_B"]["recall"],
                "F1_B":                rpt["content_B"]["F1"],
                "BLEU-4_B":            rpt["content_B"]["BLEU-4"],
                "local_align_score_B": rpt["content_B"]["local_align_score"],

                # structure A
                "headings_count_A":    rpt["structure_A"]["headings_count"],
                "headings_percent_A":  rpt["structure_A"]["headings_percent"],
                "figures_count_A":     rpt["structure_A"]["figures_count"],
                "tables_count_A":      rpt["structure_A"]["tables_count"],

                # structure B
                "headings_count_B":    rpt["structure_B"]["headings_count"],
                "headings_percent_B":  rpt["structure_B"]["headings_percent"],
                "figures_count_B":     rpt["structure_B"]["figures_count"],
                "tables_count_B":      rpt["structure_B"]["tables_count"],

                # coherence A
                "pct_chunks_end_at_sentence_A": rpt["coherence_A"]["pct_chunks_end_at_sentence"],
                "pct_sentences_split_A":        rpt["coherence_A"]["pct_sentences_split"],
                "mean_tokens_A":                rpt["coherence_A"]["length_stats"]["mean_tokens"],
                "std_tokens_A":                 rpt["coherence_A"]["length_stats"]["std_tokens"],
                "max_tokens_A":                 rpt["coherence_A"]["length_stats"]["max_tokens"],

                # coherence B
                "pct_chunks_end_at_sentence_B": rpt["coherence_B"]["pct_chunks_end_at_sentence"],
                "pct_sentences_split_B":        rpt["coherence_B"]["pct_sentences_split"],
                "mean_tokens_B":                rpt["coherence_B"]["length_stats"]["mean_tokens"],
                "std_tokens_B":                 rpt["coherence_B"]["length_stats"]["std_tokens"],
                "max_tokens_B":                 rpt["coherence_B"]["length_stats"]["max_tokens"],

                # runtime A
                "time_per_page_A":    rpt["runtime_A"]["time_per_page_s"],
                "pages_per_second_A": rpt["runtime_A"]["pages_per_second"],

                # runtime B
                "time_per_page_B":    rpt["runtime_B"]["time_per_page_s"],
                "pages_per_second_B": rpt["runtime_B"]["pages_per_second"],
            }
            writer.writerow(row)
