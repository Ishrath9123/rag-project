# filters.py
# ----------
# This file handles filtering and graceful failure in our RAG app.
#
# The retrieval problem:
# ChromaDB always returns results — even when nothing is relevant.
# If you ask "What is the best pizza topping?", ChromaDB will still return
# the 3 "most similar" tech documents, even though none of them actually
# match. Without filtering, we'd generate a nonsense answer from unrelated docs.
#
# The solution: similarity thresholds.
# We only keep documents where the distance (dissimilarity) is below a
# cutoff value. Documents that are too far away get dropped.
#
# Graceful degradation:
# When no documents pass the filter, we don't crash — we return a helpful
# message explaining what happened. This is called "graceful degradation."

from config import SIMILARITY_THRESHOLD

RETRYABLE_STATUS_CODES = {429, 500, 503, 504}


def is_retryable_api_error(error):
    """Return True for temporary Gemini/API failures worth retrying."""
    code = getattr(error, "code", None)
    if code in RETRYABLE_STATUS_CODES:
        return True

    error_str = str(error).lower()
    return any(
        phrase in error_str
        for phrase in (
            "503",
            "429",
            "500",
            "504",
            "rate limit",
            "quota",
            "resource_exhausted",
            "service unavailable",
            "overloaded",
            "unavailable",
        )
    )


def filter_by_threshold(documents, distances, threshold=SIMILARITY_THRESHOLD):
    """
    Keep only documents that are similar enough to the query.

    Args:
        documents:  List of document strings from ChromaDB.
        distances:  List of L2 distance values (one per document).
        threshold:  Max allowed distance. Documents with distance above
                    this are considered too dissimilar to be useful.

    Returns:
        (filtered_documents, filtered_distances) — only the passing pairs.
    """
    # TODO (Week 14): Implement similarity threshold filtering.
    #
    # --- The RAG concept ---
    # This is where we enforce quality control on our retrieved context.
    # A document with distance 0.3 is very similar to the query — keep it.
    # A document with distance 1.8 is barely related — discard it.
    # If we passed irrelevant documents to the LLM, it might hallucinate
    # or give a confused answer. Filtering keeps the context clean.
    #
    # Steps:
    #   1. Create two empty lists: filtered_docs and filtered_distances
    #   2. Loop through documents and distances together using zip()
    #   3. For each (doc, distance) pair: if distance <= threshold, keep both
    #   4. Return (filtered_docs, filtered_distances)
    #
    filtered_docs = []
    filtered_distances = []
    for doc, distance in zip(documents, distances):
        if distance <= threshold:
            filtered_docs.append(doc)
            filtered_distances.append(distance)
    return filtered_docs, filtered_distances


def has_relevant_results(documents):
    """Return True if at least one document passed the threshold filter."""
    return len(documents) > 0


def get_fallback_response():
    """
    Return a helpful message when no relevant documents were found.

    Returns:
        A string explaining why no answer was generated and what to try instead.
    """
    # TODO (Week 14): Write a graceful fallback message.
    #
    # --- The RAG concept ---
    # When the filter removes all documents, there's nothing for the LLM to
    # base an answer on. Instead of returning an empty string or letting the
    # LLM make something up from nothing, we stop early and tell the user
    # what happened. This is called "graceful degradation."
    #
    # Write a user-friendly message that:
    #   - Explains no relevant information was found
    #   - Suggests the user try rephrasing or asks about supported topics
    #     (Python, machine learning, databases, APIs, AI concepts)
    #
    return (
        "I couldn't find any relevant information in the knowledge base for your question. "
        "Try rephrasing your question or ask about supported topics like Python, "
        "machine learning, databases, APIs, or AI concepts."
    )


def handle_api_error(error):
    """
    Convert a raw API exception into a user-friendly message.

    Args:
        error: An Exception caught from a Gemini API call.

    Returns:
        A plain-English string describing what went wrong.
    """
    error_str = str(error).lower()
    code = getattr(error, "code", None)

    if code in RETRYABLE_STATUS_CODES or is_retryable_api_error(error):
        return (
            "The AI service is temporarily unavailable due to rate limits or high demand. "
            "Please wait 30 seconds and try again."
        )
    elif "api key" in error_str or "authentication" in error_str or "invalid_api_key" in error_str:
        return (
            "There's a problem with the API key. "
            "Please check that your GEMINI_API_KEY in the .env file is correct."
        )
    else:
        return (
            "An unexpected error occurred while generating a response. "
            "Please try again."
        )
