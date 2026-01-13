# 🏗️ Architecture & Files Explanation

**Simple guide to understanding how the Agentic Certificate Evaluator works**

---

## 🔄 How It Works (Text Flow with Code)

**Simple 10-Step Process with Actual Code Locations:**

### **Step 1: User types message** 👤
```python
# File: main.py (line 80)
user_input = input("\n💬 You: ")
```
**What happens:** Terminal waits for you to type

---

### **Step 2: Message stored** 💾
```python
# File: main.py (line 95)
state["conversation"].last_user_message = user_input
```
**What happens:** Your message saved in conversation state

---

### **Step 3: Agent activated** 🤖
```python
# File: main.py (line 99)
state = graph.invoke(state)

# Which internally calls:
# File: agent/agent.py (line 16)
def agent_node(state):
```
**What happens:** Graph triggers the agent's brain

---

### **Step 4: Context built** 📋
```python
# File: agent/agent.py (lines 22-55)
decision_prompt = f"""
{AGENT_DECISION_PROMPT}

User Input:
{state["conversation"].last_user_message}

Certificate State:
- Extracted Fields COUNT: {extracted_count}
- Fields: {list(state["certificate"].extracted_fields.keys())}

Evaluation State:
- Criteria COUNT: {criteria_count}
- Criteria: {state["evaluation"].criteria}

Conversation State:
- History Length: {history_count}
- Recent Context: {state["conversation"].conversation_history[-2:]}
"""
```
**What happens:** Builds a detailed prompt with ALL context

---

### **Step 5: LLM decides** 🧠
```python
# File: agent/agent.py (lines 58-59)
llm = get_llm_with_fallback()
response = llm.invoke(decision_prompt)
```
**What happens:** Sends prompt to Groq/Gemini, LLM analyzes and decides

---

### **Step 6: LLM returns decision** 📨
```python
# File: agent/agent.py (lines 64-70)
decision = safe_json_parse(
    response.content,
    fallback={
        "next_action": "explain",
        "reason": "Failed to parse decision",
        "uncertainty": "LLM response was not valid JSON",
    },
)
```
**What happens:** Parses LLM's JSON response like:
```json
{
  "next_action": "extract_information",
  "reason": "User wants to extract certificate data",
  "uncertainty": ""
}
```

---

### **Step 7: Action routed** 🎯
```python
# File: agent/agent.py (lines 85-103)
action = decision.get("next_action", "explain")

if action == "answer_from_state":
    return answer_from_state(state)
elif action == "show_history":
    return show_history(state)
elif action == "extract_information":
    return extract_information(state)  # ← This one gets called!
elif action == "rescore":
    return rescore_certificate(state)
# ... etc
```
**What happens:** Routes to the action LLM chose

---

### **Step 8: Action executes** ⚙️
```python
# File: actions/extract.py (lines 7-234)
def extract_information(state):
    # Check if data already exists
    if extracted_fields and not force_reextract:
        # Use cached data
        state["conversation"].last_agent_message = "✓ Using cached..."
    else:
        # Actually extract
        result = llm.invoke(prompt)
        data = safe_json_parse(result.content)
        state["certificate"].extracted_fields = data["fields"]
        state["certificate"].confidence = data["confidence"]
        state["conversation"].last_agent_message = "✓ Extracted..."
    
    return state
```
**What happens:** Extracts data, updates state, creates response

---

### **Step 9: State saved** 💾
```python
# File: main.py (line 148)
state_manager.save_state(state)

# Which calls:
# File: utils/state_manager.py (lines 22-66)
def save_state(self, state):
    state_data = {
        "certificate": {...},
        "evaluation": {...},
        "conversation": {...}
    }
    with open(self.current_session_file, "w") as f:
        json.dump(state_data, f, indent=2)
```
**What happens:** Saves entire state to `session_data/current_session.json`

---

### **Step 10: Response shown** 📤
```python
# File: main.py (line 103)
print(f"\n🤖 Agent: {state['conversation'].last_agent_message}")
```
**What happens:** Shows agent's response to you

---

**🎯 Key Insight:** Steps 5-6 are where the "agentic magic" happens - the LLM decides, not hardcoded logic!

---

## 📊 Visual Flowchart

```
┌─────────────────────┐
│   👤 User Input     │
│  "Score my cert"    │
└──────────┬──────────┘
           │
           ▼
┌──────────────────────────┐
│  📝 Store in State       │
│  state.last_user_message │
└──────────┬───────────────┘
           │
           ▼
┌────────────────────────────────────┐
│  🤖 agent_node()                   │
│  • Reads current state             │
│  • Builds decision prompt          │
│  • Includes conversation history   │
└──────────┬─────────────────────────┘
           │
           ▼
┌────────────────────────────────────┐
│  🧠 LLM (Groq/Gemini)              │
│  ⚡ DECIDES NEXT ACTION ⚡          │  ← AGENTIC CORE!
│  Analyzes: state + user + history  │
│  Returns: action + reasoning       │
└──────────┬─────────────────────────┘
           │
           ▼
┌────────────────────────────────────┐
│  🎯 Action Router                  │
│  if action == "extract":           │
│     → extract_information()        │
│  elif action == "score":           │
│     → rescore_certificate()        │
│  elif action == "explain":         │
│     → explain_decision()           │
│  etc...                            │
└──────────┬─────────────────────────┘
           │
           ▼
┌────────────────────────────────────┐
│  ⚙️ Action Executes                │
│  • Reads state                     │
│  • Performs task                   │
│  • Updates state                   │
│  • Generates response              │
└──────────┬─────────────────────────┘
           │
           ▼
┌────────────────────────────────────┐
│  💾 Save State                     │
│  Auto-save to disk (persistence)   │
└──────────┬─────────────────────────┘
           │
           ▼
┌────────────────────────────────────┐
│  📤 Show Response                  │
│  "✓ Certificate scored: 85/100"    │
└──────────┬─────────────────────────┘
           │
           │ Loop back ↻
           └─────────────────────────┐
                                     │
                                     ▼
                              ┌─────────────┐
                              │ Next Turn   │
                              └─────────────┘
```

---

## 🗂️ Project Structure & File Explanations

### **Root Files**

#### `main.py`
**What it does:** Terminal interface for the agent  
**Simple:** Chat loop that takes user input, calls agent, shows response

#### `app.py`
**What it does:** Web UI (Streamlit) for the agent  
**Simple:** Pretty web interface with chat, state display, and buttons

#### `README.md`
**What it does:** Documentation for HR/users  
**Simple:** Explains how the system works, architecture, and features

#### `TRANSCRIPT.md`
**What it does:** Sample conversation showing agent capabilities  
**Simple:** Example chat showing all features in action

#### `TESTING.md`
**What it does:** Guide for testing the agent  
**Simple:** How to verify everything works correctly

#### `TASK_FULFILLMENT.md`
**What it does:** Maps requirements to implementation  
**Simple:** Proves we completed every task requirement

#### `requirements.txt`
**What it does:** List of Python packages needed  
**Simple:** Install these to run the project

---

### **📁 `/state` - State Management**

Stores all information that needs to persist across conversation turns.

#### `global_state.py`
**What it does:** Container for all 3 state types  
**Simple:** Holds certificate + evaluation + conversation state together

#### `certificate_state.py`
**What it does:** Stores certificate data  
**Contains:**
- `raw_text` - Original certificate content
- `extracted_fields` - Parsed data (name, GPA, etc.)
- `confidence` - How sure we are about each field (0.0-1.0)

#### `evaluation_state.py`
**What it does:** Stores scoring information  
**Contains:**
- `criteria` - What to evaluate (GPA, Research, etc.) with weights
- `scores` - Score for each criterion
- `final_score` - Overall weighted score (0-100)

#### `conversation_state.py`
**What it does:** Stores conversation context  
**Contains:**
- `last_user_message` - What user just said
- `last_agent_message` - What agent just replied
- `last_reason` - Why agent chose that action
- `uncertainty` - What's unclear or missing
- `conversation_history` - All past exchanges (for memory)
- `reasoning_history` - All past decisions (for explainability)

---

### **📁 `/actions` - What the Agent Can Do**

Each file is one action the agent can choose.

#### `extract.py` - Extract Information
**What it does:** Parses certificate text to extract data  
**When used:** User asks to extract OR data doesn't exist  
**Smart feature:** Uses cached data if already extracted (efficient!)

#### `validate.py` - Validate Criteria
**What it does:** Sets or changes evaluation criteria  
**When used:** User says "Evaluate based on GPA, Research..."  
**Example:** "Set criteria: GPA 40%, Research 30%, Leadership 30%"

#### `score.py` - Calculate Score
**What it does:** Calculates weighted score based on criteria  
**When used:** User asks to score/rate/evaluate  
**Smart feature:** Maps criteria to extracted fields intelligently

#### `explain.py` - Explain Decisions
**What it does:** Explains why agent chose previous action  
**When used:** User asks "why", "explain", or says "hello"/"bye"  
**Smart feature:** Handles greetings, farewells, and gratitude

#### `answer.py` - Answer from State
**What it does:** Answers questions using existing data  
**When used:** User asks about already-extracted information  
**Smart feature:** Auto-extracts if data missing, otherwise uses cache

#### `clarify.py` - Ask for Clarification
**What it does:** Requests missing information  
**When used:** User wants to score but no criteria set  
**Example:** "⚠️ No criteria set. Please specify what to evaluate."

#### `compare.py` - Compare Certificates
**What it does:** Compares multiple certificates (placeholder)  
**When used:** User asks to compare  
**Note:** Currently single-cert mode, ready for expansion

#### `pause.py` - Pause Execution
**What it does:** Waits for user confirmation  
**When used:** User says "pause" or "wait"  
**Shows:** Current state summary while paused

#### `history.py` - Show History
**What it does:** Displays full conversation history  
**When used:** User says "history" or "show past messages"  
**Shows:** All exchanges, actions taken, statistics

---

### **📁 `/agent` - Decision-Making Brain**

#### `agent.py`
**What it does:** THE CORE - Makes all decisions  
**How it works:**
1. Builds decision prompt with full context
2. Calls LLM to decide action
3. Routes to chosen action
4. Updates reasoning history

**Key function:** `agent_node(state)` - called every turn

#### `prompts.py`
**What it does:** Instructions for the LLM  
**Contains:**
- When to use each action
- Decision rules
- Examples of good decisions
- Guidelines for agentic behavior

---

### **📁 `/graph` - LangGraph Setup**

#### `graph.py`
**What it does:** Builds the LangGraph state machine  
**How it works:**
- Creates one agent node
- Sets entry/exit points
- Manages state flow

**Why simple graph?** Single node = pure agentic (no workflow!)

---

### **📁 `/llm` - LLM Integration**

#### `llm_client.py`
**What it does:** Connects to LLM (Groq/Gemini)  
**Features:**
- Tries multiple Groq models (llama-3.3-70b, llama-3.1-8b, gemma2-9b)
- Falls back to Gemini if Groq fails
- Handles rate limits gracefully

**Models available:**
1. `llama-3.3-70b-versatile` (primary - most capable)
2. `llama-3.1-8b-instant` (fast, high limits)
3. `gemma2-9b-it` (alternative)
4. `gemini-2.0-flash-exp` (fallback)

#### `json_utils.py`
**What it does:** Safely parses LLM JSON responses  
**Why needed:** LLMs sometimes return malformed JSON  
**Features:**
- 4 fallback strategies
- Extracts JSON from markdown
- Handles common errors

---

### **📁 `/utils` - Helper Functions**

#### `state_manager.py`
**What it does:** Saves/loads state to/from disk  
**Features:**
- Auto-saves after every turn
- Loads previous session on startup
- Keeps session history
- Enables persistence across restarts

---

### **📁 `/data` - Test Data**

#### `certificate.txt`
**What it does:** Sample university certificate  
**Contains:** UC Berkeley CS degree for Sarah Chen  
**Purpose:** Test data demonstrating all features

---

### **📁 `__pycache__` - Python Cache**

**What it is:** Auto-generated by Python  
**Contains:** Compiled Python bytecode (`.pyc` files)  
**Purpose:** Makes Python run faster on subsequent runs  
**Do you need it?** NO - Python creates it automatically  
**Should you commit it?** NO - add to `.gitignore`  
**Can you delete it?** YES - Python will recreate it  

**Simple explanation:** Python's way of "remembering" compiled code to speed things up. Ignore it!

---

## 🔄 Multi-Model Fallback Strategy

**Problem:** Free LLMs have rate limits  
**Solution:** Multiple models with automatic fallback

### **Current Setup in `llm_client.py`:**

```python
Priority Order:
1. llama-3.3-70b-versatile (Groq) ← Try first
2. llama-3.1-8b-instant (Groq)    ← If #1 rate limited
3. gemma2-9b-it (Groq)            ← If #2 rate limited
4. gemini-2.0-flash-exp (Google)  ← Last resort
```

### **How It Works:**

1. System tries `llama-3.3-70b-versatile` (best model)
2. If rate limit hit → automatically tries `llama-3.1-8b-instant`
3. If that's also limited → tries `gemma2-9b-it`
4. If all Groq models exhausted → falls back to Gemini
5. User never sees errors - seamless switching!

### **Rate Limits (Groq Free Tier):**

- Per minute: 30 requests
- Per day: Varies by model
- Token limits: Different per model

**Note:** Each model has separate quota, so switching = fresh limits!

---

## 🎯 Key Design Principles

### **1. Agentic (Not Workflow)**
- ❌ No: Extract → Validate → Score (fixed sequence)
- ✅ Yes: LLM decides what to do based on context

### **2. State as Living Context**
- Previous outputs are NOT thrown away
- Agent checks existing data before re-doing work
- Efficient and treats state as truth

### **3. User Controls Everything**
- Can skip steps, reorder, go back
- Can challenge and correct agent
- Can change criteria mid-evaluation

### **4. Explainable AI**
- Every decision has a reason
- User can ask "why" anytime
- Full reasoning trail maintained

### **5. Persistent Memory**
- State saved to disk automatically
- Survives restarts
- No data loss between sessions

---

## 🚀 Quick Start

**Terminal:**
```bash
python main.py
```

**Web UI:**
```bash
streamlit run app.py
```

**Try:**
- "Extract information from my certificate"
- "Set criteria: GPA 40%, Research 30%, Leadership 30%"
- "Score my certificate"
- "Explain your last action"

---

## 📝 Summary

**In 3 sentences:**

> The agent receives user input, sends it to an LLM with full context (state + history), and the LLM decides which action to take. The chosen action executes, updates the state, and generates a response. This repeats every turn with no fixed workflow - pure intelligence!

**Why it's agentic:**
- LLM chooses actions dynamically
- No hardcoded sequences
- Context-aware decisions
- User controls flow

**Why it's production-ready:**
- Persistent state (survives restarts)
- Multiple LLM fallbacks (handles rate limits)
- Error handling (safe JSON parsing)
- Full explainability (reasoning trail)
- Professional UI (terminal + web)

---

## 📚 All Libraries Used - Simple Explanations

### **Core Libraries:**

#### **1. `langchain`** 
**What:** Framework for building LLM applications  
**Why:** Provides structure for connecting to LLMs  
**Used in:** `llm/llm_client.py`  
**Simple:** The foundation that lets us talk to AI models

#### **2. `langchain-google-genai`**
**What:** LangChain integration for Google Gemini  
**Why:** Lets us use Gemini LLM (free)  
**Used in:** `llm/llm_client.py` (line 55)  
**Simple:** Connects to Google's AI

#### **3. `langchain-groq`**
**What:** LangChain integration for Groq  
**Why:** Lets us use Groq's fast LLMs (free)  
**Used in:** `llm/llm_client.py` (line 39)  
**Simple:** Connects to Groq's super-fast AI

#### **4. `langgraph`**
**What:** State machine framework for agents  
**Why:** Manages state flow between actions  
**Used in:** `graph/graph.py`  
**Simple:** Keeps track of conversation state

#### **5. `pydantic`**
**What:** Data validation library  
**Why:** Ensures state has correct structure  
**Used in:** All `state/*.py` files  
**Simple:** Makes sure data is organized properly

#### **6. `python-dotenv`**
**What:** Loads environment variables from `.env` file  
**Why:** Keeps API keys secure  
**Used in:** `llm/llm_client.py` (line 6), `app.py` (line 17)  
**Simple:** Loads secrets safely

#### **7. `streamlit`**
**What:** Web UI framework  
**Why:** Creates the pretty web interface  
**Used in:** `app.py` (entire file)  
**Simple:** Makes the beautiful web app

---

### **Python Built-in Libraries:**

#### **8. `json`**
**What:** Parse JSON data  
**Why:** LLM returns decisions as JSON  
**Used in:** Many files for parsing responses  
**Simple:** Reads AI's structured responses

#### **9. `os`**
**What:** Operating system functions  
**Why:** Read environment variables, file paths  
**Used in:** `llm/llm_client.py`, `utils/state_manager.py`  
**Simple:** Talks to your computer

#### **10. `pathlib`**
**What:** Modern file path handling  
**Why:** Better than string paths  
**Used in:** `utils/state_manager.py` (line 4)  
**Simple:** Handles file locations smartly

#### **11. `datetime`**
**What:** Date and time functions  
**Why:** Timestamp sessions  
**Used in:** `utils/state_manager.py` (line 3)  
**Simple:** Knows what time it is

#### **12. `typing`**
**What:** Type hints (Dict, List, etc.)  
**Why:** Makes code clearer and safer  
**Used in:** All state files  
**Simple:** Labels what type of data we're using

#### **13. `re`**
**What:** Regular expressions  
**Why:** Pattern matching in JSON parsing  
**Used in:** `llm/json_utils.py` (line 2)  
**Simple:** Finds patterns in text

---

### **📦 Quick Reference Table:**

| Library | Purpose | Simple Explanation |
|---------|---------|-------------------|
| **LangChain** | LLM Framework | Talks to AI models |
| **LangGraph** | State Manager | Manages conversation state |
| **Pydantic** | Data Validator | Keeps data organized |
| **Streamlit** | Web UI | Makes pretty interface |
| **python-dotenv** | Config Loader | Loads API keys securely |
| **langchain-groq** | Groq Integration | Connects to Groq AI |
| **langchain-google-genai** | Gemini Integration | Connects to Google AI |
| **json** | Data Parser | Reads AI responses |
| **os/pathlib** | File Handler | Saves/loads files |
| **datetime** | Time Functions | Timestamps sessions |
| **typing** | Type Hints | Labels data types |
| **re** | Pattern Matching | Finds text patterns |

---

### **🎯 In One Sentence:**

> "We use **LangChain** to talk to **Groq/Gemini** LLMs, **LangGraph** to manage state, **Pydantic** to structure data, **Streamlit** for the UI, and built-in Python libraries for basic operations like JSON parsing and file handling."

---

**A Project Done By MEEZAN using LangChain, LangGraph, Groq, and Gemini**