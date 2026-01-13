from llm.json_utils import safe_json_parse
from llm.llm_client import get_llm

llm = get_llm()


def extract_information(state):
    # Check if data is already extracted (caching for performance)
    if state["certificate"].extracted_fields and not any(word in state["conversation"].last_user_message.lower() for word in ["re-extract", "extract again", "update", "correct", "change"]):
        # Use cached data
        extracted_fields = state["certificate"].extracted_fields
        confidence = state["certificate"].confidence
        
        extracted_summary = "\n".join(
            [f"  - {k}: {v}" for k, v in extracted_fields.items()]
        )
        confidence_summary = "\n".join(
            [f"  - {k}: {v * 100:.1f}%" for k, v in confidence.items()]
        )
        
        state["conversation"].last_agent_message = (
            f"✓ Using previously extracted certificate information:\n{extracted_summary}\n\n"
            f"Confidence levels:\n{confidence_summary}\n\n"
            f"(Data was cached from previous extraction. Say 're-extract' to force fresh extraction.)"
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
    
    # Proceed with fresh extraction
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

    # Extract fields
    extracted_fields = data.get("fields", {})
    confidence_raw = data.get("confidence", {})

    # Normalize confidence values to ensure they are floats
    confidence = {}
    for key, value in confidence_raw.items():
        try:
            # Handle various formats: float, int, string, dict
            if isinstance(value, dict):
                # If it's a dict, try to extract a numeric value
                if "value" in value:
                    confidence[key] = float(value["value"])
                elif "score" in value:
                    confidence[key] = float(value["score"])
                else:
                    # Default to 0.5 if we can't parse
                    confidence[key] = 0.5
            elif isinstance(value, (int, float)):
                # Ensure it's between 0 and 1
                conf_val = float(value)
                if conf_val > 1.0:
                    conf_val = conf_val / 100.0  # Convert percentage to decimal
                confidence[key] = max(0.0, min(1.0, conf_val))
            elif isinstance(value, str):
                # Try to parse string as float
                conf_val = float(value.strip().replace("%", ""))
                if conf_val > 1.0:
                    conf_val = conf_val / 100.0
                confidence[key] = max(0.0, min(1.0, conf_val))
            else:
                confidence[key] = 0.5
        except (ValueError, TypeError):
            # If parsing fails, default to 0.5
            confidence[key] = 0.5

    # Check if parsing failed or no data extracted
    if not extracted_fields and not confidence:
        state["conversation"].last_agent_message = (
            "❌ Failed to extract information. Please try rephrasing your request.\n\n"
            "The LLM response could not be parsed correctly."
        )
        return state

    state["certificate"].extracted_fields = extracted_fields
    state["certificate"].confidence = confidence

    # Set agent response message
    if extracted_fields:
        extracted_summary = "\n".join(
            [f"  - {k}: {v}" for k, v in extracted_fields.items()]
        )
    else:
        extracted_summary = "  - No fields extracted"

    if confidence:
        confidence_summary = "\n".join(
            [f"  - {k}: {v * 100:.1f}%" for k, v in confidence.items()]
        )
    else:
        confidence_summary = "  - No confidence data"

    state["conversation"].last_agent_message = (
        f"✓ Extracted certificate information:\n{extracted_summary}\n\n"
        f"Confidence levels:\n{confidence_summary}"
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
