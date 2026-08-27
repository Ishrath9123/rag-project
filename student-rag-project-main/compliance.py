# compliance.py
# ---------------
# Week 18: Metadata tagging and automated redaction for sensitive data.
#
# This module identifies sensitive patterns, attaches metadata tags,
# and redacts sensitive text before logging or external API calls.

import logging
import re

logger = logging.getLogger("rag_app")

# Metadata tag scheme
SENSITIVITY_PUBLIC = "public"
SENSITIVITY_INTERNAL = "internal"
SENSITIVITY_CONFIDENTIAL = "confidential"
SENSITIVITY_RESTRICTED = "restricted"

DATA_TYPE_PII = "PII"
DATA_TYPE_PHI = "PHI"
DATA_TYPE_FINANCIAL = "financial"
DATA_TYPE_OPERATIONAL = "operational"

SOURCE_USER_INPUT = "user_input"
SOURCE_DOCUMENT = "document"
SOURCE_MODEL_OUTPUT = "model_output"

EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
PHONE_PATTERN = re.compile(r"\b(?:\+?1[-.\s]?)?(?:\(\d{3}\)|\d{3})[-.\s]?\d{3}[-.\s]?\d{4}\b")
SSN_PATTERN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
CREDIT_CARD_PATTERN = re.compile(r"\b(?:\d{4}[-\s]?){3}\d{4}\b")
PHI_KEYWORDS = re.compile(
    r"\b(?:patient|diagnosis|medical record|prescription|hipaa)\b",
    re.IGNORECASE,
)

REDACTION_LABEL = "[REDACTED]"


def detect_sensitive_types(text):
    """Return a list of detected sensitive data types in the text."""
    if not text:
        return []

    detected = []
    if EMAIL_PATTERN.search(text) or SSN_PATTERN.search(text):
        detected.append(DATA_TYPE_PII)
    if PHONE_PATTERN.search(text):
        detected.append(DATA_TYPE_PII)
    if CREDIT_CARD_PATTERN.search(text):
        detected.append(DATA_TYPE_FINANCIAL)
    if PHI_KEYWORDS.search(text):
        detected.append(DATA_TYPE_PHI)

    return list(dict.fromkeys(detected))


def classify_sensitivity(text, source):
    """Classify sensitivity level based on content and source."""
    detected = detect_sensitive_types(text)

    if DATA_TYPE_PHI in detected or DATA_TYPE_FINANCIAL in detected:
        return SENSITIVITY_RESTRICTED
    if DATA_TYPE_PII in detected:
        return SENSITIVITY_CONFIDENTIAL
    if source == SOURCE_USER_INPUT:
        return SENSITIVITY_INTERNAL
    return SENSITIVITY_PUBLIC


def build_metadata(text, source):
    """
    Build metadata tags for a piece of text.

    Tags:
      - sensitivity: public / internal / confidential / restricted
      - data_type:   PII / PHI / financial / operational
      - source:      user_input / document / model_output
    """
    detected = detect_sensitive_types(text)
    if detected:
        data_type = detected[0]
    else:
        data_type = DATA_TYPE_OPERATIONAL

    return {
        "sensitivity": classify_sensitivity(text, source),
        "data_type": data_type,
        "source": source,
    }


def redact_sensitive_text(text):
    """Mask or remove sensitive patterns from text."""
    if not text:
        return text

    redacted = EMAIL_PATTERN.sub(REDACTION_LABEL, text)
    redacted = PHONE_PATTERN.sub(REDACTION_LABEL, redacted)
    redacted = SSN_PATTERN.sub(REDACTION_LABEL, redacted)
    redacted = CREDIT_CARD_PATTERN.sub(REDACTION_LABEL, redacted)
    return redacted


def safe_log(message, text=""):
    """Log a message with sensitive data redacted."""
    if text:
        logger.info("%s | %s", message, redact_sensitive_text(text))
    else:
        logger.info(message)


def tag_documents(documents):
    """Attach metadata to each document at ingest time."""
    return [build_metadata(doc, SOURCE_DOCUMENT) for doc in documents]


def contains_sensitive_data(text):
    """Return True if the text contains patterns we should redact."""
    return bool(detect_sensitive_types(text))
