# structural_metrics.py

from collections import Counter

def extract_headings_from_gt(gt_json):
    """
    From your combined GT (wrapped as {"pages": [...]}) pull out all blocks
    whose form-category or label indicates a section header.
    """
    headings = []
    for page in gt_json.get("pages", []):
        # GT uses 'form' list of dicts
        for block in page.get("form", []):
            text = block.get("text", "").strip()
            # GT may label header blocks with 'category' or 'label'
            label = block.get("category", "").lower() or block.get("label", "").lower()
            if "header" in label or "heading" in label:
                if text:
                    headings.append(text)
    return headings

def extract_headings_from_pred(pred_json):
    """
    Predicted JSON uses pages→regions, with 'category' ending in '-header'.
    """
    headings = []
    for page in pred_json.get("pages", []):
        for region in page.get("regions", []):
            cat = region.get("category", "").lower()
            if cat.endswith("-header") or "heading" in cat:
                text = region.get("text", "").strip()
                if text:
                    headings.append(text)
    return headings

def compare_headings(gt_list, pred_list):
    """
    Simple matching: count how many predicted headings exactly appear in GT.
    Returns (matched_count, matched_count/len(gt_list)).
    """
    gt_set = set(gt_list)
    matched = sum(1 for h in pred_list if h in gt_set)
    pct = matched / len(gt_list) if gt_list else 0.0
    return matched, pct

def count_figures_tables_from_gt(gt_json):
    """
    If your GT 'form' blocks include figure/table categories you can count them here.
    Otherwise, we skip GT counts (so downstream code will see zero GT figures/tables).
    """
    figs = tables = 0
    for page in gt_json.get("pages", []):
        for block in page.get("form", []):
            label = block.get("category", "").lower() or block.get("label", "").lower()
            if "figure" in label:
                figs += 1
            if "table" in label:
                tables += 1
    return figs, tables

def count_figures_tables_from_pred(pred_json):
    """
    Pipeline ⇒ pages→regions with category 'figure' or 'table'.
    """
    figs = tables = 0
    for page in pred_json.get("pages", []):
        for region in page.get("regions", []):
            cat = region.get("category", "").lower()
            if cat.startswith("figure"):
                figs += 1
            if cat.startswith("table"):
                tables += 1
    return figs, tables

def compute_structural_metrics(pred_json, gt_json):
    """
    Returns a dict:
      {
        "headings_count":   int,   # # predicted headings
        "headings_percent": float, # % of GT headings captured
        "figures_count":    int,   # # predicted figures
        "tables_count":     int    # # predicted tables
      }
    """
    # 1. Headings
    gt_headings   = extract_headings_from_gt(gt_json)
    pred_headings = extract_headings_from_pred(pred_json)
    matched, pct  = compare_headings(gt_headings, pred_headings)

    # 2. Figures/Tables (we don't currently compare GT counts for these)
    figs_pred, tables_pred = count_figures_tables_from_pred(pred_json)

    return {
        "headings_count":   len(pred_headings),
        "headings_percent": pct,
        "figures_count":    figs_pred,
        "tables_count":     tables_pred
    }
