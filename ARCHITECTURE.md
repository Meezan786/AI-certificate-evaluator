# 🏗️ Architecture & Files Explanation

**Simple guide to understanding how the Agentic Certificate Evaluator works**

---

## 🔄 How It Works (Text Flow)

**Simple 10-Step Process:**

1. **User types message** → System receives input (e.g., "Extract my certificate")
2. **Message stored** → Saved in `state["conversation"].last_user_message`
3. **Agent activated** → `agent_node()` function called
4. **Context built** → Combines current state + user message + history
5. **LLM decides** → Groq/Gemini analyzes context and picks best action
6. **LLM returns decision** → JSON: `{"next_action": "extract", "reason": "...", "uncertainty": "..."}`
7. **Action routed** → System calls chosen action (e.g., `extract_information()`)
8. **Action executes** → Performs task, updates state, creates response
9. **State saved** → Auto-saved to disk for persistence
10. **Response shown** → User sees result, loop repeats

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

**Built with ❤️ using LangChain, LangGraph, Groq, and Gemini**