# Agentic Certificate Evaluation AI

A fully agentic, chat-driven Certificate Evaluation AI Agent that reasons dynamically based on user interaction and evolving context. This system implements true agentic behavior - no predefined workflows or pipelines.

## 🎯 Core Concept

This is **not** a traditional workflow system. The agent **dynamically decides** its next action at runtime based on:
- Current conversation context
- Certificate state (extracted data, confidence levels)
- Evaluation state (criteria, scores, weights)
- User intent and conversation history
- Reasoning from previous decisions

The agent can skip steps, revisit decisions, reorder operations, and adapt to user corrections - all through natural conversation.

---

## 🏗️ Architecture

### Agent State Model

The system maintains three interconnected state spaces that evolve continuously:

#### 1. **Certificate State** (`state/certificate_state.py`)
```python
{
    "raw_text": str,              # Original certificate content
    "extracted_fields": Dict,      # Parsed information (name, GPA, degree, etc.)
    "confidence": Dict             # Confidence level for each extracted field (0.0-1.0)
}
```

**Purpose**: Tracks what we know about the certificate, how it was extracted, and our confidence in that information.

#### 2. **Evaluation State** (`state/evaluation_state.py`)
```python
{
    "criteria": Dict[str, float],  # Evaluation criteria with weights (sum to 1.0)
    "scores": Dict[str, float],    # Score for each criterion
    "final_score": float           # Weighted final score (0-100)
}
```

**Purpose**: Manages evaluation logic - what criteria matter, how much they're weighted, and current scoring results.

#### 3. **Conversation State** (`state/conversation_state.py`)
```python
{
    "last_user_message": str,
    "last_agent_message": str,
    "last_reason": str,                    # Why the agent chose its last action
    "uncertainty": str,                    # What's unclear or missing
    "last_user_intent": str,
    "pending_confirmation": bool,
    "conversation_history": List[Dict],    # Full dialogue for context persistence
    "reasoning_history": List[Dict]        # Agent's decision trail for explainability
}
```

**Purpose**: Maintains conversational context, tracks reasoning, enables the agent to reference past exchanges, and ensures explainability.

---

## 🧠 Step-Selection Logic (Agentic Core)

### How the Agent Decides

At each turn, the agent:

1. **Receives user input** and current state (certificate + evaluation + conversation)
2. **Reasons about context** using an LLM-powered decision prompt
3. **Selects the most appropriate action** from available options:
   - `extract_information` - Parse certificate data
   - `validate_criteria` - Set/modify evaluation criteria
   - `rescore` - Calculate scores based on current criteria
   - `explain` - Justify previous decisions
   - `ask_clarification` - Request missing information
   - `compare_certificates` - Compare multiple certificates
   - `pause` - Wait for user confirmation

4. **Executes the chosen action** and updates all relevant state
5. **Returns control** to the user - no predetermined next step

### Key Implementation: `agent/agent.py`

```python
def agent_node(state):
    # Build context-aware prompt
    decision_prompt = f"""
    [Agent Decision Prompt]
    User Input: {state.conversation.last_user_message}
    Certificate State: {state.certificate}
    Evaluation State: {state.evaluation}
    Conversation History: {state.conversation.conversation_history[-3:]}
    """
    
    # LLM decides the next action
    response = llm.invoke(decision_prompt)
    decision = json.loads(response.content)  # {"next_action": "...", "reason": "...", "uncertainty": "..."}
    
    # Record reasoning for explainability
    state.conversation.last_reason = decision["reason"]
    state.conversation.uncertainty = decision["uncertainty"]
    state.conversation.reasoning_history.append(decision)
    
    # Route to selected action (NOT a fixed workflow)
    if decision["next_action"] == "extract_information":
        return extract_information(state)
    elif decision["next_action"] == "validate_criteria":
        return validate_criteria(state)
    # ... other actions ...
```

**This is agentic** because:
- ✅ No if/then workflow logic
- ✅ Agent decides based on holistic context
- ✅ Can jump to any action at any time
- ✅ Reasoning is explicit and traceable

---

## 🔄 Context Handling Strategy

### Persistent State Across Turns

**Challenge**: How does the agent "remember" previous decisions, user corrections, and evolving context?

**Solution**: Multi-layered state persistence

1. **Conversation History** (`conversation_history`)
   - Stores every user input and agent response
   - Tagged with the action that was taken
   - Enables the agent to reference "what we discussed 3 turns ago"

2. **Reasoning History** (`reasoning_history`)
   - Records why each action was chosen
   - Captures uncertainty at each step
   - Allows the agent to explain its decision-making process

3. **Living State Updates**
   - `extracted_fields` and `confidence` are incrementally updated
   - `criteria` can be modified mid-conversation
   - `scores` are recalculated on-demand, not on schedule

### Example Context Flow

```
Turn 1:
User: "Extract my degree information"
Agent decides: extract_information
State update: extracted_fields += {degree, gpa, institution}

Turn 2:
User: "Actually, my GPA is 3.8, not 3.7"
Agent decides: extract_information (re-extract with correction)
State update: extracted_fields[gpa] = 3.8, confidence[gpa] = 1.0

Turn 3:
User: "Now evaluate it based on GPA and Institution"
Agent decides: validate_criteria
State update: criteria = {gpa: 0.5, institution: 0.5}

Turn 4:
User: "Score it"
Agent decides: rescore
State update: Uses criteria weights, recalculates final_score

Turn 5:
User: "Why did you score it that way?"
Agent decides: explain
Output: References reasoning_history and criteria from Turn 3-4
```

### Why This Works

- **No reset between turns**: State accumulates rather than restarting
- **Agent references history**: Can say "Based on your earlier correction..."
- **User can challenge**: "Change the GPA weight to 70%" triggers re-evaluation without restarting
- **Explainable**: Every decision has a recorded reason

---

## 🛠️ Technical Implementation

### Technology Stack
- **LLM**: Google Gemini 1.5 Flash (free tier)
- **Framework**: LangChain + LangGraph
- **State Management**: Pydantic models for type safety
- **Language**: Python 3.8+

### Project Structure
```
Agentic-Certificate-Evaluator/
├── main.py                     # Entry point, conversation loop
├── data/
│   └── certificate.txt         # Certificate test data
├── state/
│   ├── global_state.py         # Unified state container
│   ├── certificate_state.py    # Certificate data model
│   ├── evaluation_state.py     # Evaluation criteria & scores
│   └── conversation_state.py   # Conversation context & history
├── agent/
│   ├── agent.py                # Core decision-making node
│   └── prompts.py              # Agent decision prompt
├── actions/
│   ├── extract.py              # Extract certificate information
│   ├── validate.py             # Set/validate criteria
│   ├── score.py                # Score based on criteria
│   ├── explain.py              # Explain decisions
│   ├── clarify.py              # Ask for clarification
│   ├── compare.py              # Compare certificates
│   └── pause.py                # Pause for confirmation
├── graph/
│   └── graph.py                # LangGraph state graph
└── llm/
    └── llm_client.py           # LLM initialization
```

### Key Design Decisions

1. **Single Agent Node**: One `agent_node` makes all decisions - avoids complex multi-agent orchestration
2. **LangGraph for State**: Uses `StateGraph` to manage state persistence, not for workflow routing
3. **Action Functions**: Each action is self-contained, updates state, and returns
4. **JSON Decision Format**: Agent returns structured decisions for reliability
5. **Error Handling**: Safe JSON parsing with fallbacks to prevent crashes

### Error Handling & Edge Cases

The system is designed to be robust and handle various failure scenarios:

#### LLM Response Failures
- **Invalid JSON**: `safe_json_parse()` attempts multiple parsing strategies:
  - Direct JSON parsing
  - Extract from markdown code blocks
  - Find JSON objects in text
  - Clean common formatting issues
- **Fallback Decision**: If parsing fails, defaults to `explain_decision` action with clear error message
- **Rate Limiting**: Automatic fallback between Groq models, then to Gemini if needed

#### Action Execution Failures
- **Missing Data**: Actions check for required state before proceeding
- **Invalid Actions**: Unknown actions route to `explain_decision` with guidance
- **Network Issues**: LLM calls have timeouts and retry logic

#### State Corruption
- **Validation**: Pydantic models ensure type safety
- **Recovery**: State manager can restore from backup if corruption detected
- **Graceful Degradation**: System continues with partial state if needed

#### User Input Issues
- **Ambiguous Requests**: Agent asks for clarification when intent unclear
- **Missing Context**: References conversation history to fill gaps
- **Corrections**: User can override any extracted data or decisions

---

## 🚀 Usage

### Setup
```bash
# Install dependencies
pip install langchain langchain-google-genai pydantic

# Set API key
export GEMINI_API_KEY="your-api-key"

# Add certificate data
echo "Your certificate content" > data/certificate.txt
```

### Run
```bash
python main.py
```

### Example Interaction
```
You: Extract information from my certificate
Agent: ✓ Extracted certificate information:
       - Name: John Doe
       - Degree: Bachelor of Science
       - GPA: 3.75
       - Institution: MIT
       Confidence levels:
       - Name: 95.0%
       - Degree: 92.0%
       - GPA: 88.0%
       - Institution: 98.0%

You: Evaluate based on GPA (40%), Institution (30%), and Degree Type (30%)
Agent: ✓ Set 3 evaluation criteria with weights
       Active Evaluation Criteria:
       - GPA: weight=0.40
       - Institution: weight=0.30
       - Degree Type: weight=0.30

You: Score it
Agent: ✓ Certificate re-scored based on current criteria:
       - GPA: 75.0 (weight: 0.4)
       - Institution: 88.2 (weight: 0.3)
       - Degree Type: 76.6 (weight: 0.3)
       **Final Weighted Score: 78.9/100**

You: Why did you score GPA at 75?
Agent: **Decision Explanation:**
       Reason: User requested explanation of scoring logic
       Extracted Data: GPA: 3.75 (confidence: 88.0%)
       The GPA score reflects the confidence level and extracted value...
```

---

## 🎓 Agentic Principles Demonstrated

### 1. Dynamic Action Selection
❌ **Not**: If user says X, do Y (workflow)
✅ **Is**: Based on context (user intent + current state + history), what action makes most sense right now?

### 2. Stateful Reasoning
❌ **Not**: Treat each turn independently
✅ **Is**: Every decision builds on previous context; agent "remembers" and references past exchanges

### 3. User-Driven Control
❌ **Not**: Fixed evaluation pipeline
✅ **Is**: User can intervene, reorder steps, change criteria, challenge results at any point

### 4. Explainability
❌ **Not**: Black box that outputs scores
✅ **Is**: Agent explains why it chose each action, what's uncertain, and how it scored

### 5. Context Evolution
❌ **Not**: State resets between interactions
✅ **Is**: State accumulates and evolves; previous outputs become living context for future decisions

---

## 📊 Sample Chat Transcript

See `TRANSCRIPT.md` for a full example demonstrating:
- Initial extraction
- User correction of extracted data
- Criteria modification mid-conversation
- Re-evaluation without resetting state
- Explanation of reasoning
- Step reordering based on user requests

---

## 🧪 Testing

The system uses a real university certificate (placed in `data/certificate.txt`) as test data. This demonstrates:
- Context ingestion from unstructured text
- Incremental reasoning across multiple turns
- Partial re-evaluation (e.g., changing one criterion and re-scoring)
- Explainable outcomes through conversation

---

## 🔮 Future Enhancements

- Multi-certificate comparison with relative scoring
- Persistent storage (database) for long-term memory
- Advanced criteria validation (e.g., "Is this GPA competitive for grad school?")
- Confidence-based clarification triggers
- Integration with external verification APIs

---

## 📝 License

MIT License - Feel free to use and modify for your own agentic AI projects.

---

## 🤝 Contributing

This is a demonstration project for agentic AI principles. Contributions welcome to enhance:
- More sophisticated step-selection logic
- Better uncertainty quantification
- Richer conversation memory management
- Additional evaluation criteria types

---

**Built with ❤️ to showcase true agentic AI - no workflows, just intelligent reasoning.**