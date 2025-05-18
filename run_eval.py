import os
import argparse
from evaluate_pipelines import evaluate_documents, load_combined_gt

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--pdf_dir",
        default="input_pdfs",
        help="Directory containing your input PDF files",
    )
    parser.add_argument(
        "--gt_combined",
        default="combined_outputs/jsons/all_jsons_combined.json",
        help="Path to your single combined ground-truth JSON",
    )
    parser.add_argument(
        "--output_dir",
        default="reports",
        help="Directory where per-doc JSON & summary CSV will be written",
    )
    args = parser.parse_args()

    # ensure output subfolders exist
    os.makedirs(os.path.join(args.output_dir, "json"), exist_ok=True)
    os.makedirs(os.path.join(args.output_dir, "csv"), exist_ok=True)

    # load the single combined GT once
    combined_gt = load_combined_gt(args.gt_combined)

    # collect all PDFs
    docs = sorted(
        f for f in os.listdir(args.pdf_dir)
        if f.lower().endswith(".pdf")
    )

    # run evaluation
    evaluate_documents(
        docs,
        pdf_dir=args.pdf_dir,
        combined_gt=combined_gt,
        report_json_dir=os.path.join(args.output_dir, "json"),
        report_csv_path=os.path.join(args.output_dir, "csv", "summary.csv"),
    )

    print("ALl jobs done!!!!!")

