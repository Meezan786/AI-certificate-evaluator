def rescore_certificate(state):
    """
    Rescore certificate based on evaluation criteria and weights.
    Intelligently maps criteria to extracted fields.
    """
    scores = {}

    # Check if evaluation criteria are defined
    if state["evaluation"].criteria:
        # Intelligent field mapping for common criteria
        field_mapping = {
            "GPA": ["Cumulative GPA", "Major GPA", "GPA"],
            "gpa": ["Cumulative GPA", "Major GPA", "GPA"],
            "Academic Performance": [
                "Cumulative GPA",
                "Major GPA",
                "Total Units Completed",
            ],
            "academics": ["Cumulative GPA", "Major GPA"],
            "Research": ["research", "publication", "paper", "lab"],
            "research experience": ["research", "publication", "paper", "lab"],
            "Leadership": ["leadership", "president", "vice president", "captain"],
            "leadership": ["leadership", "president", "vice president", "captain"],
            "Honors": ["honors", "dean's list", "award", "distinction"],
            "honors": ["honors", "dean's list", "award", "distinction"],
            "Institution": ["University", "institution", "college"],
            "institution": ["University", "institution", "college"],
            "Degree": ["Degree", "degree type"],
            "degree type": ["Degree", "degree type"],
        }

        total_weight = sum(state["evaluation"].criteria.values())

        for criterion, weight in state["evaluation"].criteria.items():
            # Try to find matching fields
            criterion_lower = criterion.lower()
            matched_fields = []

            # Check if criterion has a mapping
            if criterion in field_mapping:
                keywords = field_mapping[criterion]
            elif criterion_lower in field_mapping:
                keywords = field_mapping[criterion_lower]
            else:
                # Use criterion name as keyword
                keywords = [criterion]

            # Find matching extracted fields
            for field_name, field_value in state[
                "certificate"
            ].extracted_fields.items():
                for keyword in keywords:
                    if (
                        keyword.lower() in field_name.lower()
                        or keyword.lower() in str(field_value).lower()
                    ):
                        if field_name in state["certificate"].confidence:
                            matched_fields.append(field_name)
                            break

            # Calculate score based on matched fields
            if matched_fields:
                # Use average confidence of matched fields
                confidences = []
                for field in matched_fields:
                    try:
                        conf = float(state["certificate"].confidence[field])
                        confidences.append(conf)
                    except (ValueError, TypeError):
                        continue

                if confidences:
                    avg_confidence = sum(confidences) / len(confidences)
                    # Score = confidence * 100 * weight
                    scores[criterion] = avg_confidence * 100 * weight
                else:
                    scores[criterion] = 50.0 * weight
            else:
                # No matching fields found - check if data exists in certificate text
                cert_text = state["certificate"].raw_text.lower()
                criterion_in_text = False

                for keyword in keywords:
                    if keyword.lower() in cert_text:
                        criterion_in_text = True
                        break

                if criterion_in_text:
                    # Data exists but not extracted - use moderate score
                    scores[criterion] = 70.0 * weight
                else:
                    # Data not found - low score
                    scores[criterion] = 30.0 * weight

        # Calculate weighted final score
        if total_weight > 0:
            state["evaluation"].final_score = sum(scores.values()) / total_weight
        else:
            state["evaluation"].final_score = 0.0

        state["evaluation"].scores = scores

        # Create detailed response message
        score_details = "\n".join(
            [
                f"  - {k}: {v:.1f} (weight: {state['evaluation'].criteria[k]:.2f})"
                for k, v in scores.items()
            ]
        )

        state["conversation"].last_agent_message = (
            f"✓ Certificate re-scored based on current criteria:\n\n"
            f"{score_details}\n\n"
            f"**Final Weighted Score: {state['evaluation'].final_score:.1f}/100**"
        )
    else:
        # Fallback: Use confidence-based scoring
        if state["certificate"].confidence:
            for k, conf in state["certificate"].confidence.items():
                try:
                    conf_value = float(conf)
                    scores[k] = conf_value * 100
                except (ValueError, TypeError):
                    continue

            if scores:
                state["evaluation"].scores = scores
                state["evaluation"].final_score = sum(scores.values()) / len(scores)

                score_details = "\n".join(
                    [f"  - {k}: {v:.1f}" for k, v in scores.items()]
                )

                state["conversation"].last_agent_message = (
                    f"✓ Certificate scored based on confidence levels:\n\n"
                    f"{score_details}\n\n"
                    f"**Average Score: {state['evaluation'].final_score:.1f}/100**\n\n"
                    f"Note: No evaluation criteria set. Using confidence-based scoring.\n"
                    f"You can set criteria by saying: 'Evaluate based on [criterion1, criterion2]'"
                )
            else:
                state["conversation"].last_agent_message = (
                    "❌ Cannot score certificate: Invalid confidence data.\n"
                    "Please extract information first."
                )
                state["evaluation"].final_score = 0.0
        else:
            state["conversation"].last_agent_message = (
                "❌ Cannot score certificate: No extracted information or criteria available.\n"
                "Please extract information first."
            )
            state["evaluation"].final_score = 0.0

    # Update conversation history
    state["conversation"].conversation_history.append(
        {
            "user": state["conversation"].last_user_message,
            "agent": state["conversation"].last_agent_message,
            "action": "rescore",
        }
    )

    return state
