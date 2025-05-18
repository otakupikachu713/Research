# retrieval_eval.py

from sentence_transformers import SentenceTransformer
import numpy as np

# Load a pre-trained embedding model for sentence embeddings
embedder = SentenceTransformer('all-MiniLM-L6-v2')  # example model

def embed_chunks(chunks):
    """Compute embeddings for a list of chunk texts."""
    return embedder.encode(chunks, convert_to_numpy=True)

def retrieval_recall_at_k(query, ref_chunks, ref_embeddings, cand_chunks, cand_embeddings, k=5):
    """
    Compute Recall@K for a query: whether any of the top-K retrieved chunks from candidate set
    contain the correct answer chunk from a reference set.
    `ref_chunks` and `ref_embeddings` represent the ground-truth reference chunks (or the better pipeline),
    `cand_chunks` and `cand_embeddings` represent chunks from the pipeline being evaluated.
    """
    # Embed the query
    q_vec = embedder.encode([query], convert_to_numpy=True)[0]
    # Determine the "ground truth" relevant chunk index from reference by max similarity
    sims_to_ref = np.dot(ref_embeddings, q_vec)
    true_idx = int(np.argmax(sims_to_ref))
    true_chunk = ref_chunks[true_idx]
    # Retrieve top-K from candidate chunks
    sims_to_cand = np.dot(cand_embeddings, q_vec)
    top_k_idx = np.argsort(sims_to_cand)[::-1][:k]
    retrieved_chunks = [cand_chunks[i] for i in top_k_idx]
    # Check if the true relevant chunk (or its content) is among retrieved_chunks
    relevant_retrieved = any(true_chunk[:50] in chunk for chunk in retrieved_chunks)  # simplistic check by content overlap
    return 1 if relevant_retrieved else 0

# (Optional) function to perform QA with an LLM given retrieved context
def answer_query_with_context(query, context_chunks, llm_answer_fn):
    """
    Feeds the query and provided context to an LLM (via llm_answer_fn) to get an answer.
    llm_answer_fn should be a function that takes (query, context) and returns an answer string.
    """
    context_text = " ".join(context_chunks)
    return llm_answer_fn(query, context_text)

# Example usage:
# chunks_A = [...]  # Pipeline A chunks
# chunks_B = [...]  # Pipeline B chunks
# emb_A = embed_chunks(chunks_A)
# emb_B = embed_chunks(chunks_B)
# query = "What are the main categories of RAG described in the paper?"
# # Assume Pipeline B (PyMuPDF) chunks are reference for content
# recall_at5_A = retrieval_recall_at_k(query, chunks_B, emb_B, chunks_A, emb_A, k=5)
# recall_at5_B = retrieval_recall_at_k(query, chunks_B, emb_B, chunks_B, emb_B, k=5)  # Pipeline B vs itself (should be 1 if query answer exists)
