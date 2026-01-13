def answer_from_state(state):
    """
    Answer user questions directly from existing state without re-extracting.
    This demonstrates treating previous outputs as living context.
    If no data exists, automatically extracts it first - true intelligence!
    """
    user_message = state["conversation"].last_user_message.lower()

    # INTELLIGENT AUTO-EXTRACTION: If no data exists, extract it automatically!
    extracted_fields = state["certificate"].extracted_fields
    auto_extracted = False

    if not extracted_fields:
        # Import here to avoid circular dependency
        from actions.extract import extract_information

        state["conversation"].last_agent_message = (
            "🔄 **No data extracted yet - let me extract it for you automatically!**\n\n"
            "Extracting certificate information now...\n"
        )

        # Auto-extract the certificate
        state = extract_information(state)
        auto_extracted = True

        # After extraction, continue answering the question
        extracted_fields = state["certificate"].extracted_fields

        # If extraction failed, return with error
        if not extracted_fields:
            state["conversation"].last_agent_message = (
                "❌ **Failed to extract certificate information.**\n\n"
                "Please check that the certificate file exists and has content.\n"
                "File location: `data/certificate.txt`"
            )
            return state

        # Update reasoning to reflect auto-extraction
        state["conversation"].last_reason = (
            "User asked for information that wasn't extracted yet. "
            "Auto-extracted certificate data first, then answered the question. "
            "This demonstrates intelligent proactive behavior - understanding user intent and fulfilling it automatically."
        )

        # Prepend auto-extraction notice to the answer
        state["conversation"].last_agent_message = (
            "✓ **Auto-extracted certificate data!**\n\n"
            + state["conversation"].last_agent_message
            + "\n\n---\n\n"
        )

    # Continue with normal flow
    confidence = state["certificate"].confidence
    criteria = state["evaluation"].criteria
    scores = state["evaluation"].scores
    final_score = state["evaluation"].final_score

    response = ""

    # Detect what information user is asking for
    asking_about = {
        "name": ["name", "student name", "whose certificate", "who is"],
        "gpa": ["gpa", "grade point", "grades", "cumulative gpa", "major gpa"],
        "degree": ["degree", "what degree", "major", "field of study"],
        "university": [
            "university",
            "institution",
            "school",
            "college",
            "where did",
        ],
        "graduation": [
            "graduation",
            "graduated",
            "conferred",
            "completion date",
            "when did",
        ],
        "score": [
            "what score",
            "current score",
            "total score",
            "final score",
            "rating",
        ],
        "criteria": ["what criteria", "evaluation criteria", "what factors"],
        "honors": ["honors", "awards", "distinctions", "achievements"],
        "research": ["research", "publications", "papers", "lab"],
        "leadership": ["leadership", "president", "vice president", "officer"],
    }

    # Find what user is asking about
    found_topic = None
    for topic, keywords in asking_about.items():
        if any(keyword in user_message for keyword in keywords):
            found_topic = topic
            break

    # Answer based on what they're asking
    if found_topic == "name" and "Name" in extracted_fields:
        name = extracted_fields["Name"]
        conf = confidence.get("Name", 0.0) * 100
        response = f"📝 The student's name is **{name}** (confidence: {conf:.1f}%)\n\n"

    elif found_topic == "gpa":
        gpa_fields = {k: v for k, v in extracted_fields.items() if "gpa" in k.lower()}
        if gpa_fields:
            response = "📊 **GPA Information:**\n"
            for field, value in gpa_fields.items():
                conf = confidence.get(field, 0.0) * 100
                response += f"  - {field}: {value} (confidence: {conf:.1f}%)\n"
            response += "\n"
        else:
            response = "⚠️ No GPA information found in extracted data.\n\n"

    elif found_topic == "degree" and "Degree" in extracted_fields:
        degree = extracted_fields["Degree"]
        conf = confidence.get("Degree", 0.0) * 100
        response = f"🎓 The degree is **{degree}** (confidence: {conf:.1f}%)\n\n"

    elif found_topic == "university":
        uni_fields = {
            k: v
            for k, v in extracted_fields.items()
            if "university" in k.lower() or "college" in k.lower()
        }
        if uni_fields:
            response = "🏛️ **Institution Information:**\n"
            for field, value in uni_fields.items():
                conf = confidence.get(field, 0.0) * 100
                response += f"  - {field}: {value} (confidence: {conf:.1f}%)\n"
            response += "\n"
        else:
            response = "⚠️ No university information found in extracted data.\n\n"

    elif found_topic == "graduation":
        grad_fields = {
            k: v
            for k, v in extracted_fields.items()
            if "conferred" in k.lower() or "graduation" in k.lower()
        }
        if grad_fields:
            response = "📅 **Graduation Information:**\n"
            for field, value in grad_fields.items():
                conf = confidence.get(field, 0.0) * 100
                response += f"  - {field}: {value} (confidence: {conf:.1f}%)\n"
            response += "\n"
        else:
            response = "⚠️ No graduation date found in extracted data.\n\n"

    elif found_topic == "score":
        if final_score > 0:
            response = f"⭐ **Current Evaluation Score: {final_score:.1f}/100**\n\n"
            if scores:
                response += "**Score Breakdown:**\n"
                for criterion, score in scores.items():
                    weight = criteria.get(criterion, 0.0)
                    response += f"  - {criterion}: {score:.1f} (weight: {weight:.2f})\n"
                response += "\n"
        else:
            response = (
                "⚠️ No score calculated yet. "
                "Please set criteria and run scoring first.\n\n"
            )

    elif found_topic == "criteria":
        if criteria:
            response = "🎯 **Active Evaluation Criteria:**\n"
            for criterion, weight in criteria.items():
                response += f"  - {criterion}: weight={weight:.2f}\n"
            response += "\n"
        else:
            response = "⚠️ No evaluation criteria set yet.\n\n"

    elif found_topic in ["honors", "research", "leadership"]:
        # Search in all extracted fields for this topic
        relevant_fields = {
            k: v
            for k, v in extracted_fields.items()
            if found_topic in k.lower() or found_topic in str(v).lower()
        }
        if relevant_fields:
            response = f"🏆 **{found_topic.title()} Information:**\n"
            for field, value in relevant_fields.items():
                conf = confidence.get(field, 0.0) * 100
                response += f"  - {field}: {value} (confidence: {conf:.1f}%)\n"
            response += "\n"
        else:
            # Check raw certificate text
            if found_topic in state["certificate"].raw_text.lower():
                response = (
                    f"ℹ️ {found_topic.title()} information exists in the certificate "
                    f"but hasn't been extracted yet.\n"
                    f"Would you like me to extract it?\n\n"
                )
            else:
                response = (
                    f"⚠️ No {found_topic} information found in the certificate.\n\n"
                )

    else:
        # General question - provide overview of available data
        if extracted_fields:
            response = "📋 **Available Information from Certificate:**\n"
            for field, value in list(extracted_fields.items())[:5]:
                conf = confidence.get(field, 0.0) * 100
                response += f"  - {field}: {value} (confidence: {conf:.1f}%)\n"
            if len(extracted_fields) > 5:
                response += f"  ... and {len(extracted_fields) - 5} more fields\n"
            response += "\n💡 Ask me about a specific field for more details!\n\n"
        else:
            response = (
                "⚠️ No certificate data extracted yet.\n"
                "Say 'Extract information from my certificate' to begin.\n\n"
            )

    # Add note about using existing data
    if "Auto-extracted" not in state["conversation"].last_agent_message:
        response += "\n\n✓ *Answered from existing state (no re-extraction needed)*"

    # If we auto-extracted, append the answer to the extraction message
    if "Auto-extracted" in state["conversation"].last_agent_message:
        state["conversation"].last_agent_message += response
    else:
        state["conversation"].last_agent_message = response

    # Update conversation history
    state["conversation"].conversation_history.append(
        {
            "user": state["conversation"].last_user_message,
            "agent": state["conversation"].last_agent_message,
            "action": "answer_from_state",
        }
    )

    return state
