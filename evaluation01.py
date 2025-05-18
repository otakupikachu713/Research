import os
import json
import content_metrics as content_metrics
import coherence_metrics as coherence_metrics
import structural_metrics as structural_metrics


def evaluate_outputs(outputs_base_dir, annotations_dir):
    """
    Compare pipeline outputs against ground truth annotations and print a comparative report.
    """
    # List all ground truth annotation files in the annotations directory
    if not os.path.isdir(annotations_dir):
        print(f"Annotations directory not found: {annotations_dir}")
        return
    gt_files = [f for f in os.listdir(annotations_dir) if f.endswith(".json")]
    if not gt_files:
        print(f"No ground truth files found in {annotations_dir}")
        return
    gt_files.sort()
    # Document IDs (base filenames without extension)
    doc_ids = [os.path.splitext(f)[0] for f in gt_files]
    # Prepare structure to hold scores for each doc, pipeline, and input type
    scores = {}
    missing_outputs = []  # to track any missing pipeline outputs
    for doc_id in doc_ids:
        gt_path = os.path.join(annotations_dir, doc_id + ".json")
        with open(gt_path, 'r', encoding='utf-8') as f:
            gt_data = json.load(f)
        scores[doc_id] = {"haonan01": {}, "james01": {}}
        # Compute metrics for each pipeline and input type
        for pipeline in ["haonan01", "james01"]:
            for input_type in ["pdf", "image"]:
                pred_path = os.path.join(outputs_base_dir, pipeline, input_type, doc_id + ".json")
                if not os.path.exists(pred_path):
                    # If output is missing, record warning and skip metrics
                    missing_outputs.append((pipeline, input_type, doc_id))
                    scores[doc_id][pipeline][input_type] = None
                    continue
                with open(pred_path, 'r', encoding='utf-8') as pf:
                    pred_data = json.load(pf)
                # Use the metrics modules to evaluate (assuming each returns a numeric score)
                try:
                    content_score = content_metrics.evaluate(gt_data, pred_data)
                except Exception as e:
                    content_score = None
                    print(f"Error computing content metrics for {doc_id} ({pipeline}, {input_type}): {e}")
                try:
                    coherence_score = coherence_metrics.evaluate(gt_data, pred_data)
                except Exception as e:
                    coherence_score = None
                    print(f"Error computing coherence metrics for {doc_id} ({pipeline}, {input_type}): {e}")
                try:
                    structural_score = structural_metrics.evaluate(gt_data, pred_data)
                except Exception as e:
                    structural_score = None
                    print(f"Error computing structural metrics for {doc_id} ({pipeline}, {input_type}): {e}")
                scores[doc_id][pipeline][input_type] = {
                    "content": content_score,
                    "coherence": coherence_score,
                    "structural": structural_score
                }
    # Print warnings for any missing outputs
    if missing_outputs:
        for (pipeline, input_type, doc_id) in set(missing_outputs):
            print(f"Warning: Missing output for {pipeline} {input_type.upper()} on document {doc_id}")
        print()  # blank line after warnings
    # Prepare and print markdown tables for PDF and image comparisons
    print("## PDF Inputs Evaluation")
    print(
        "| Document | Content (haonan01) | Content (james01) | Coherence (haonan01) | Coherence (james01) | Structural (haonan01) | Structural (james01) |")
    print(
        "|----------|-------------------|-------------------|----------------------|----------------------|------------------------|------------------------|")
    # For average calculations
    pdf_counts = {"haonan01": 0, "james01": 0}
    pdf_sums = {
        "haonan01": {"content": 0, "coherence": 0, "structural": 0},
        "james01": {"content": 0, "coherence": 0, "structural": 0}
    }
    for doc_id in doc_ids:
        # Only include row if both pipelines have results for PDF
        if scores[doc_id]["haonan01"].get("pdf") is None or scores[doc_id]["james01"].get("pdf") is None:
            continue
        h_scores = scores[doc_id]["haonan01"]["pdf"]
        j_scores = scores[doc_id]["james01"]["pdf"]
        # Format scores or use "N/A" if score is missing/None
        h_content = f"{h_scores['content']:.3f}" if isinstance(h_scores['content'], (int, float)) and h_scores[
            'content'] is not None else "N/A"
        j_content = f"{j_scores['content']:.3f}" if isinstance(j_scores['content'], (int, float)) and j_scores[
            'content'] is not None else "N/A"
        h_coh = f"{h_scores['coherence']:.3f}" if isinstance(h_scores['coherence'], (int, float)) and h_scores[
            'coherence'] is not None else "N/A"
        j_coh = f"{j_scores['coherence']:.3f}" if isinstance(j_scores['coherence'], (int, float)) and j_scores[
            'coherence'] is not None else "N/A"
        h_str = f"{h_scores['structural']:.3f}" if isinstance(h_scores['structural'], (int, float)) and h_scores[
            'structural'] is not None else "N/A"
        j_str = f"{j_scores['structural']:.3f}" if isinstance(j_scores['structural'], (int, float)) and j_scores[
            'structural'] is not None else "N/A"
        print(f"| {doc_id} | {h_content} | {j_content} | {h_coh} | {j_coh} | {h_str} | {j_str} |")
        # Accumulate sums for averages (count how many docs have numeric scores)
        if isinstance(h_scores['content'], (int, float)):
            pdf_sums["haonan01"]["content"] += h_scores['content'];
            pdf_counts["haonan01"] += 1
        if isinstance(h_scores['coherence'], (int, float)):
            pdf_sums["haonan01"]["coherence"] += h_scores['coherence']
        if isinstance(h_scores['structural'], (int, float)):
            pdf_sums["haonan01"]["structural"] += h_scores['structural']
        if isinstance(j_scores['content'], (int, float)):
            pdf_sums["james01"]["content"] += j_scores['content'];
            pdf_counts["james01"] += 1
        if isinstance(j_scores['coherence'], (int, float)):
            pdf_sums["james01"]["coherence"] += j_scores['coherence']
        if isinstance(j_scores['structural'], (int, float)):
            pdf_sums["james01"]["structural"] += j_scores['structural']
    print("\n## Image Inputs Evaluation")
    print(
        "| Document | Content (haonan01) | Content (james01) | Coherence (haonan01) | Coherence (james01) | Structural (haonan01) | Structural (james01) |")
    print(
        "|----------|-------------------|-------------------|----------------------|----------------------|------------------------|------------------------|")
    img_counts = {"haonan01": 0, "james01": 0}
    img_sums = {
        "haonan01": {"content": 0, "coherence": 0, "structural": 0},
        "james01": {"content": 0, "coherence": 0, "structural": 0}
    }
    for doc_id in doc_ids:
        if scores[doc_id]["haonan01"].get("image") is None or scores[doc_id]["james01"].get("image") is None:
            continue
        h_scores = scores[doc_id]["haonan01"]["image"]
        j_scores = scores[doc_id]["james01"]["image"]
        h_content = f"{h_scores['content']:.3f}" if isinstance(h_scores['content'], (int, float)) and h_scores[
            'content'] is not None else "N/A"
        j_content = f"{j_scores['content']:.3f}" if isinstance(j_scores['content'], (int, float)) and j_scores[
            'content'] is not None else "N/A"
        h_coh = f"{h_scores['coherence']:.3f}" if isinstance(h_scores['coherence'], (int, float)) and h_scores[
            'coherence'] is not None else "N/A"
        j_coh = f"{j_scores['coherence']:.3f}" if isinstance(j_scores['coherence'], (int, float)) and j_scores[
            'coherence'] is not None else "N/A"
        h_str = f"{h_scores['structural']:.3f}" if isinstance(h_scores['structural'], (int, float)) and h_scores[
            'structural'] is not None else "N/A"
        j_str = f"{j_scores['structural']:.3f}" if isinstance(j_scores['structural'], (int, float)) and j_scores[
            'structural'] is not None else "N/A"
        print(f"| {doc_id} | {h_content} | {j_content} | {h_coh} | {j_coh} | {h_str} | {j_str} |")
        if isinstance(h_scores['content'], (int, float)):
            img_sums["haonan01"]["content"] += h_scores['content'];
            img_counts["haonan01"] += 1
        if isinstance(h_scores['coherence'], (int, float)):
            img_sums["haonan01"]["coherence"] += h_scores['coherence']
        if isinstance(h_scores['structural'], (int, float)):
            img_sums["haonan01"]["structural"] += h_scores['structural']
        if isinstance(j_scores['content'], (int, float)):
            img_sums["james01"]["content"] += j_scores['content'];
            img_counts["james01"] += 1
        if isinstance(j_scores['coherence'], (int, float)):
            img_sums["james01"]["coherence"] += j_scores['coherence']
        if isinstance(j_scores['structural'], (int, float)):
            img_sums["james01"]["structural"] += j_scores['structural']
    # Compute average scores for each pipeline on PDFs, images, and overall
    pdf_avg = {"haonan01": {}, "james01": {}}
    img_avg = {"haonan01": {}, "james01": {}}
    overall_avg = {"haonan01": {}, "james01": {}}
    for pipeline in ["haonan01", "james01"]:
        if pdf_counts[pipeline] > 0:
            pdf_avg[pipeline]["content"] = pdf_sums[pipeline]["content"] / pdf_counts[pipeline]
            pdf_avg[pipeline]["coherence"] = pdf_sums[pipeline]["coherence"] / pdf_counts[pipeline]
            pdf_avg[pipeline]["structural"] = pdf_sums[pipeline]["structural"] / pdf_counts[pipeline]
        else:
            pdf_avg[pipeline]["content"] = None
            pdf_avg[pipeline]["coherence"] = None
            pdf_avg[pipeline]["structural"] = None
        if img_counts[pipeline] > 0:
            img_avg[pipeline]["content"] = img_sums[pipeline]["content"] / img_counts[pipeline]
            img_avg[pipeline]["coherence"] = img_sums[pipeline]["coherence"] / img_counts[pipeline]
            img_avg[pipeline]["structural"] = img_sums[pipeline]["structural"] / img_counts[pipeline]
        else:
            img_avg[pipeline]["content"] = None
            img_avg[pipeline]["coherence"] = None
            img_avg[pipeline]["structural"] = None
        # Combine PDF and image averages for overall (if available)
        total_count = 0
        total_content = total_coh = total_str = 0
        if isinstance(pdf_avg[pipeline]["content"], (int, float)):
            total_content += pdf_avg[pipeline]["content"];
            total_coh += pdf_avg[pipeline]["coherence"];
            total_str += pdf_avg[pipeline]["structural"];
            total_count += 1
        if isinstance(img_avg[pipeline]["content"], (int, float)):
            total_content += img_avg[pipeline]["content"];
            total_coh += img_avg[pipeline]["coherence"];
            total_str += img_avg[pipeline]["structural"];
            total_count += 1
        if total_count > 0:
            overall_avg[pipeline]["content"] = total_content / total_count
            overall_avg[pipeline]["coherence"] = total_coh / total_count
            overall_avg[pipeline]["structural"] = total_str / total_count
        else:
            overall_avg[pipeline]["content"] = None
            overall_avg[pipeline]["coherence"] = None
            overall_avg[pipeline]["structural"] = None
    print("\n## Summary of Average Scores")
    print(
        "| Input Type | Content (haonan01) | Content (james01) | Coherence (haonan01) | Coherence (james01) | Structural (haonan01) | Structural (james01) |")
    print(
        "|------------|-------------------|-------------------|----------------------|----------------------|------------------------|------------------------|")
    for input_type, avg_dict in [("PDF", pdf_avg), ("Image", img_avg), ("Overall", overall_avg)]:
        h_content = f"{avg_dict['haonan01']['content']:.3f}" if isinstance(avg_dict['haonan01']['content'],
                                                                           (int, float)) and avg_dict['haonan01'][
                                                                    'content'] is not None else "N/A"
        j_content = f"{avg_dict['james01']['content']:.3f}" if isinstance(avg_dict['james01']['content'],
                                                                          (int, float)) and avg_dict['james01'][
                                                                   'content'] is not None else "N/A"
        h_coh = f"{avg_dict['haonan01']['coherence']:.3f}" if isinstance(avg_dict['haonan01']['coherence'],
                                                                         (int, float)) and avg_dict['haonan01'][
                                                                  'coherence'] is not None else "N/A"
        j_coh = f"{avg_dict['james01']['coherence']:.3f}" if isinstance(avg_dict['james01']['coherence'],
                                                                        (int, float)) and avg_dict['james01'][
                                                                 'coherence'] is not None else "N/A"
        h_str = f"{avg_dict['haonan01']['structural']:.3f}" if isinstance(avg_dict['haonan01']['structural'],
                                                                          (int, float)) and avg_dict['haonan01'][
                                                                   'structural'] is not None else "N/A"
        j_str = f"{avg_dict['james01']['structural']:.3f}" if isinstance(avg_dict['james01']['structural'],
                                                                         (int, float)) and avg_dict['james01'][
                                                                  'structural'] is not None else "N/A"
        print(f"| {input_type} | {h_content} | {j_content} | {h_coh} | {j_coh} | {h_str} | {j_str} |")
