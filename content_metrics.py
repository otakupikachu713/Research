# content_metrics.py

import difflib
import math
from collections import Counter

def tokenize_text(text):
    """Basic tokenizer: lowercase and split on whitespace."""
    return text.lower().split()

def compute_fuzzy_token_metrics(ref_text, pred_text):
    """
    Compute token-level precision, recall, and F1 between reference
    and prediction using SequenceMatcher to find matching blocks.
    """
    ref_tokens = tokenize_text(ref_text)
    pred_tokens = tokenize_text(pred_text)
    matcher = difflib.SequenceMatcher(None, ref_tokens, pred_tokens)
    matching_tokens = sum(block.size for block in matcher.get_matching_blocks())

    precision = matching_tokens / len(pred_tokens) if pred_tokens else 0.0
    recall    = matching_tokens / len(ref_tokens)  if ref_tokens  else 0.0
    f1        = (2 * precision * recall / (precision + recall)
                 if (precision + recall) else 0.0)

    return precision, recall, f1

def compute_bleu_score(ref_text, pred_text, n=4):
    """
    Compute BLEU-n score by counting n-gram overlap with brevity penalty.
    """
    ref_tokens  = tokenize_text(ref_text)
    pred_tokens = tokenize_text(pred_text)

    # If prediction empty, BLEU=0 unless ref also empty -> BLEU=1
    if not pred_tokens:
        return 1.0 if not ref_tokens else 0.0

    def ngrams(tokens, n):
        return [" ".join(tokens[i:i+n]) for i in range(len(tokens)-n+1)]

    ref_counts  = Counter(ngrams(ref_tokens, n))
    pred_counts = Counter(ngrams(pred_tokens, n))

    # n-gram precision
    overlap = sum(min(pred_counts[ng], ref_counts.get(ng, 0))
                  for ng in pred_counts)
    precision_n = overlap / max(1, sum(pred_counts.values()))

    # Brevity penalty
    r, c = len(ref_tokens), len(pred_tokens)
    bp = math.exp(1 - r/c) if c < r else 1.0

    return bp * precision_n

def compute_local_alignment_score(ref_text, pred_text):
    """
    Smith-Waterman local alignment on token sequences:
    +2 for match, –1 for mismatch or gap, no negative scores.
    Returns the highest local alignment score.
    """
    ref_tokens  = tokenize_text(ref_text)
    pred_tokens = tokenize_text(pred_text)
    n, m = len(ref_tokens), len(pred_tokens)

    # scoring
    match_score      = 2
    mismatch_penalty = -1
    gap_penalty      = -1

    # DP matrix
    dp = [[0] * (m+1) for _ in range(n+1)]
    max_score = 0

    for i in range(1, n+1):
        for j in range(1, m+1):
            diag = (dp[i-1][j-1] +
                    (match_score if ref_tokens[i-1] == pred_tokens[j-1]
                     else mismatch_penalty))
            delete = dp[i-1][j] + gap_penalty
            insert = dp[i][j-1] + gap_penalty
            dp[i][j] = max(0, diag, delete, insert)
            max_score = max(max_score, dp[i][j])

    return max_score

def extract_full_text(json_dict):
    """
    Flatten all text blocks from:
      • GT pages under json_dict["pages"][*]["form"], or
      • pipeline outputs under json_dict["pages"][*]["regions"].
    """
    texts = []

    # GT combined JSON uses "form"
    for page in json_dict.get("pages", []):
        for block in page.get("form", []):
            t = block.get("text", "").strip()
            if t: texts.append(t)

    # If no "form" found, fall back to pipeline output format
    if not texts and "pages" in json_dict:
        for page in json_dict["pages"]:
            for region in page.get("regions", []):
                t = region.get("text", "").strip()
                if t: texts.append(t)

    return " ".join(texts)

def compute_content_metrics(pred_json, gt_json):
    """
    Compare pred_json vs gt_json on:
      • token-level precision, recall, F1
      • BLEU-4
      • local alignment score

    Returns a dict with keys:
      "precision", "recall", "F1", "BLEU-4", "local_align_score"
    """
    ref_text  = extract_full_text(gt_json)
    pred_text = extract_full_text(pred_json)

    p, r, f1 = compute_fuzzy_token_metrics(ref_text, pred_text)
    bleu4     = compute_bleu_score(ref_text, pred_text, n=4)
    align     = compute_local_alignment_score(ref_text, pred_text)

    return {
        "precision":        p,
        "recall":           r,
        "F1":               f1,
        "BLEU-4":           bleu4,
        "local_align_score": align
    }
