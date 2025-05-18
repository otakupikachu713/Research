# coherence_metrics.py

import spacy
import numpy as np

# Load spaCy model for sentence segmentation (English)
nlp = spacy.load("en_core_web_sm")

def chunk_boundary_stats(chunks):
    """
    Calculate two coherence metrics:
      1) % of chunk boundaries that coincide with sentence boundaries.
      2) % of sentences split across two or more chunks.
    """
    # 1. Build full text by joining chunks with single spaces
    full_text = " ".join(chunk.strip() for chunk in chunks)
    doc = nlp(full_text)

    # 2. Compute character offsets for each chunk boundary
    boundaries = []
    offset = 0
    for i, chunk in enumerate(chunks):
        length = len(chunk.strip())
        offset += length
        boundaries.append(offset)  # boundary at end-of-chunk
        # account for the space we inserted when joining
        if i < len(chunks) - 1:
            offset += 1

    # 3. Count how many boundaries align with a spaCy sentence end
    sent_ends = {sent.end_char for sent in doc.sents}
    valid_bounds = boundaries[:-1] if len(boundaries) > 1 else []
    end_at_sentence = sum(1 for b in valid_bounds if b in sent_ends)
    pct_chunks_end_at_sentence = (
        end_at_sentence / len(valid_bounds) * 100.0
        if valid_bounds else 100.0
    )

    # 4. Compute % of sentences that are split across chunks
    mapping = []
    for idx, chunk in enumerate(chunks):
        text = chunk.strip()
        mapping.extend([idx] * len(text))
        if idx < len(chunks) - 1:
            mapping.append(idx + 1)

    total_sents = 0
    split_sents = 0
    for sent in doc.sents:
        total_sents += 1
        start = sent.start_char
        end   = sent.end_char - 1  # inclusive
        if start < len(mapping) and end < len(mapping):
            if mapping[start] != mapping[end]:
                split_sents += 1

    pct_sentences_split = (
        split_sents / total_sents * 100.0
        if total_sents else 0.0
    )

    return pct_chunks_end_at_sentence, pct_sentences_split

def chunk_length_stats(chunks):
    """
    Compute basic stats on chunk lengths (in tokens & characters):
      mean, std, and max.
    """
    token_lengths = []
    char_lengths  = []

    for chunk in chunks:
        doc = nlp(chunk)
        tokens = [tok for tok in doc if not tok.is_space]
        token_lengths.append(len(tokens))
        char_lengths.append(len(chunk))

    mean_tokens = float(np.mean(token_lengths)) if token_lengths else 0.0
    std_tokens  = float(np.std(token_lengths))  if token_lengths else 0.0
    max_tokens  = int(np.max(token_lengths))   if token_lengths else 0

    mean_chars = float(np.mean(char_lengths)) if char_lengths else 0.0
    std_chars  = float(np.std(char_lengths))  if char_lengths else 0.0
    max_chars  = int(np.max(char_lengths))    if char_lengths else 0

    return {
        "mean_tokens": mean_tokens,
        "std_tokens":  std_tokens,
        "max_tokens":  max_tokens,
        "mean_chars":  mean_chars,
        "std_chars":   std_chars,
        "max_chars":   max_chars
    }

# ----------------------------------------------------------------------
# New wrapper to extract chunks and compute coherence metrics
# ----------------------------------------------------------------------

def extract_chunks_from_pred(pred_json):
    """
    Turn a pipeline’s JSON into a list of text‐chunks.
    We treat each 'region' in pages→regions as one chunk.
    """
    chunks = []
    for page in pred_json.get("pages", []):
        for region in page.get("regions", []):
            text = region.get("text", "").strip()
            if text:
                chunks.append(text)
    return chunks

def compute_coherence_metrics(pred_json, gt_json=None):
    """
    Compute coherence metrics for a pipeline output:
      - pct_chunks_end_at_sentence
      - pct_sentences_split
      - length_stats (mean/std/max tokens & chars)

    gt_json is ignored here (kept for signature consistency).
    """
    chunks = extract_chunks_from_pred(pred_json)

    pct_end, pct_split = chunk_boundary_stats(chunks)
    length_stats = chunk_length_stats(chunks)

    return {
        "pct_chunks_end_at_sentence": pct_end,
        "pct_sentences_split": pct_split,
        "length_stats": length_stats
    }
