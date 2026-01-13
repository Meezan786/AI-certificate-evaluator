import json

from llm.json_utils import safe_json_parse
from llm.llm_client import get_llm

llm = get_llm()


def extract_information(state):
    """
    Extract information from certificate.
    Intelligently handles cached data vs fresh extraction based on user intent.
    Updates reasoning to match actual behavior for consistency.
    """
    user_message = state["conversation"].last_user_message.lower()
    extracted_fields = state["certificate"].extracted_fields

    # Check if user explicitly wants re-extraction
    force_reextract = any(
        word in user_message
        for word in [
            "re-extract",
            "reextract",
            "extract again",
            "fresh extraction",
            "update data",
            "refresh data",
        ]
    )

    # If data already exists and user didn't force re-extraction
    if extracted_fields and not force_reextract:
        # Show cached data with clear explanation
        extracted_summary = "\n".join(
            [f"  - {k}: {v}" for k, v in extracted_fields.items()]
        )
        confidence_summary = "\n".join(
            [
                f"  - {k}: {v * 100:.1f}%"
                for k, v in state["certificate"].confidence.items()
            ]
        )

        state["conversation"].last_agent_message = (
            f"✓ **Using previously extracted certificate information:**\n\n{extracted_summary}\n\n"
            f"**Confidence levels:**\n{confidence_summary}\n\n"
            f"_ℹ️ Data was cached from previous extraction. Say 're-extract' to force fresh extraction._"
        )

        # Update reasoning to reflect what actually happened
        state["conversation"].last_reason = (
            "Certificate data already exists in state with good confidence levels. "
            "Using cached data for efficiency and consistency (treating previous outputs as living context). "
            "User can say 're-extract' if fresh extraction is needed."
        )

        # Update conversation history
        state["conversation"].conversation_history.append(
            {
                "user": state["conversation"].last_user_message,
                "agent": state["conversation"].last_agent_message,
                "action": "extract_information",
            }
        )

        return state

    # If no data OR forced re-extraction, proceed with actual extraction
    if force_reextract:
        extraction_notice = (
            "🔄 **Re-extracting certificate information as requested...**\n\n"
        )
    else:
        extraction_notice = ""

    prompt = f"""
Extract certificate details from the following text.
Highlight uncertainty where applicable.

Certificate:
{state["certificate"].raw_text}

User Context:
{state["conversation"].last_user_message}

Return STRICT JSON with confidence as a number between 0.0 and 1.0:
{{
  "fields": {{
    "field_name": "field_value"
  }},
  "confidence": {{
    "field_name": 0.95
  }}
}}

Example:
{{
  "fields": {{
    "Name": "John Doe",
    "GPA": "3.87",
    "Degree": "Bachelor of Science"
  }},
  "confidence": {{
    "Name": 0.98,
    "GPA": 0.95,
    "Degree": 0.97
  }}
}}

IMPORTANT: Confidence values MUST be numbers between 0.0 and 1.0, not strings or objects.
"""
    result = llm.invoke(prompt)

    # Use safe JSON parsing with fallback
    data = safe_json_parse(
        result.content,
        fallback={"fields": {}, "confidence": {}},
    )

    # Check if parsing failed
    if not data.get("fields") and not data.get("confidence"):
        state["conversation"].last_agent_message = (
            "❌ Failed to extract information. Please try rephrasing your request.\n\n"
            "The LLM response could not be parsed correctly."
        )

        # Update reasoning for failure case
        state["conversation"].last_reason = (
            "Attempted to extract certificate data but LLM response parsing failed. "
            "May need to retry or check certificate format."
        )

        return state

    state["certificate"].extracted_fields = data.get("fields", {})
    state["certificate"].confidence = data.get("confidence", {})

    # Set agent response message
    if state["certificate"].extracted_fields:
        extracted_summary = "\n".join(
            [f"  - {k}: {v}" for k, v in state["certificate"].extracted_fields.items()]
        )
    else:
        extracted_summary = "  - No fields extracted"

    if state["certificate"].confidence:
        confidence_summary = "\n".join(
            [
                f"  - {k}: {v * 100:.1f}%"
                for k, v in state["certificate"].confidence.items()
            ]
        )
    else:
        confidence_summary = "  - No confidence data"

    state["conversation"].last_agent_message = (
        f"{extraction_notice}✓ **Extracted certificate information:**\n\n{extracted_summary}\n\n"
        f"**Confidence levels:**\n{confidence_summary}"
    )

    # Update reasoning to reflect actual extraction
    if force_reextract:
        state["conversation"].last_reason = (
            "User explicitly requested re-extraction of certificate data. "
            "Performed fresh extraction to update all fields with latest parsing."
        )
    else:
        state["conversation"].last_reason = (
            "No certificate data was previously extracted in state. "
            "Performed initial extraction of certificate information with confidence levels for all detected fields."
        )

    # Update conversation history
    state["conversation"].conversation_history.append(
        {
            "user": state["conversation"].last_user_message,
            "agent": state["conversation"].last_agent_message,
            "action": "extract_information",
        }
    )

    return state
