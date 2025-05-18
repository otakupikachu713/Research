# runtime_profiler.py

import time

def profile_pipeline(process_fn, document_path):
    """
    Profile the given pipeline processing function on the specified document.
    `process_fn` should be a function that takes a document path and returns output (and processes by pages internally).
    Returns total_time, time_per_page, pages_per_second.
    """
    start_time = time.perf_counter()
    output = process_fn(document_path)  # run the pipeline on the document (could also handle multiple docs)
    end_time = time.perf_counter()
    total_time = end_time - start_time
    # Determine number of pages processed
    num_pages = 0
    # If output has page info, use that; otherwise, need to get page count from PDF
    if isinstance(output, dict):
        # Try extracting page count from known keys in output structure
        if "pages" in output:
            num_pages = len(output["pages"])
        elif "content" in output:
            num_pages = len(output["content"])
    if num_pages == 0:
        # Fallback: use a PDF library to count pages in document_path
        try:
            import fitz  # PyMuPDF
            with fitz.open(document_path) as doc:
                num_pages = doc.page_count
        except:
            num_pages = 1  # default to 1 if unknown
    time_per_page = total_time / num_pages if num_pages > 0 else float('inf')
    pages_per_sec = num_pages / total_time if total_time > 0 else 0.0
    return {
        "total_time_s": total_time,
        "time_per_page_s": time_per_page,
        "pages_per_second": pages_per_sec
    }

# Example usage:
# performance_A = profile_pipeline(run_pipelineA, "sample_document.pdf")
# performance_B = profile_pipeline(run_pipelineB, "sample_document.pdf")
