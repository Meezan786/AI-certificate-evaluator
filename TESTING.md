# Testing Guide: Agentic Certificate Evaluation AI

This guide provides comprehensive testing instructions to validate the agentic behavior of the Certificate Evaluation AI.

---

## Prerequisites

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure API Key
```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your Gemini API key
# Get free API key from: https://makersuite.google.com/app/apikey
```

### 3. Verify Certificate Data
```bash
# Check that certificate.txt has content
cat data/certificate.txt
```

---

## Running the System

```bash
python main.py
```

You should see:
```
🎓 Agentic Certificate Evaluation AI
======================================================================
This is a fully agentic system - I dynamically decide what to do based
on your requests and current context. No predefined workflows!
...
======================================================================
```

---

## Core Test Cases

### Test 1: Dynamic Action Selection ✅

**Purpose**: Verify agent chooses appropriate actions based on context, not fixed workflow

**Steps**:
```
You: Extract information from my certificate
[Agent should select: extract_information]

You: What did you just do?
[Agent should select: explain]

You: Set criteria for evaluation
[Agent should select: validate_criteria]
```

**Expected**: Agent selects different actions based on user intent, not a predetermined sequence.

**Validation**: Check that actions vary based on what you ask, proving no fixed workflow.

---

### Test 2: Non-Linear Flow (Step Reordering) ✅

**Purpose**: Verify agent can handle operations in any order

**Steps**:
```
You: Set evaluation criteria to GPA and Research
[Agent sets criteria WITHOUT extracting first]

You: Now extract my certificate information
[Agent extracts information]

You: Score it
[Agent scores using previously set criteria]
```

**Expected**: Agent handles criteria-setting before extraction (reverse of typical workflow).

**Validation**: System doesn't force extract → criteria → score order.

---

### Test 3: User Intervention and Correction ✅

**Purpose**: Verify agent accepts and incorporates user corrections

**Steps**:
```
You: Extract my certificate
[Agent extracts with some confidence levels]

You: Actually, my GPA is 3.9, not 3.8
[Agent should re-extract with correction]

You: Re-score now
[Agent should use corrected GPA]
```

**Expected**: Agent updates state based on correction without restarting.

**Validation**: Corrected value persists in subsequent operations.

---

### Test 4: Criteria Changes and Re-evaluation ✅

**Purpose**: Verify partial re-evaluation without full reset

**Steps**:
```
You: Evaluate based on GPA (50%), Institution (50%)
[Agent sets criteria]

You: Score my certificate
[Agent scores: e.g., 85.5/100]

You: Change criteria to GPA (70%), Institution (30%)
[Agent updates criteria]

You: Re-score
[Agent recalculates with new weights - score changes]
```

**Expected**: Only scores recalculate; extraction data persists unchanged.

**Validation**: Final score changes but extracted fields remain the same.

---

### Test 5: Conversation History and Context ✅

**Purpose**: Verify state persists across turns

**Steps**:
```
You: Extract my certificate
You: Set criteria to GPA and Institution
You: Score it
You: history
[Agent shows all previous exchanges]

You: Why did you score it that way?
[Agent references previous scoring decision]
```

**Expected**: Agent can reference past exchanges and explain previous decisions.

**Validation**: `history` command shows all turns; explanations reference past context.

---

### Test 6: Explainability ✅

**Purpose**: Verify agent explains reasoning and uncertainty

**Steps**:
```
You: Extract information
[Note the reasoning printed]

You: Why did you choose to extract?
[Agent explains decision-making]

You: Explain your confidence levels
[Agent justifies uncertainty assessment]
```

**Expected**: Agent provides clear reasoning for each action taken.

**Validation**: Every response includes reasoning trail (shown in first 3 turns).

---

### Test 7: Handling Uncertainty ✅

**Purpose**: Verify agent identifies and clarifies unclear information

**Steps**:
```
You: Extract only the GPA
[If certificate unclear, agent should note uncertainty]

You: [Provide ambiguous input]
[Agent should ask for clarification]
```

**Expected**: Agent flags low-confidence extractions and requests clarification when needed.

**Validation**: Check `uncertainty` field in responses for unclear data.

---

### Test 8: Pause and Confirmation ✅

**Purpose**: Verify agent can pause execution and await user confirmation

**Steps**:
```
You: Pause before scoring
[Agent should set pending_confirmation = True]

You: Proceed
[Agent continues]
```

**Expected**: Agent waits for user input before continuing.

**Validation**: `pending_confirmation` flag controls execution flow.

---

## Advanced Test Scenarios

### Scenario A: Complete Evaluation Flow

```
1. Extract certificate information
2. Challenge one extracted field
3. Set evaluation criteria with specific weights
4. Score the certificate
5. Modify criteria weights
6. Re-score
7. Ask for explanation of score change
8. View conversation history
```

**Expected**: All operations work smoothly with state persisting across all 8 turns.

---

### Scenario B: Reverse Order Testing

```
1. Set criteria FIRST (before extraction)
2. Score (should fail gracefully - no data)
3. Extract information
4. Score again (should work now)
```

**Expected**: Agent handles out-of-order operations gracefully without crashing.

---

### Scenario C: Multi-Round Corrections

```
1. Extract certificate
2. Correct field A
3. Correct field B
4. Correct field A again (overriding previous correction)
5. Score
```

**Expected**: All corrections persist; final state reflects latest corrections.

---

## Validation Checklist

Use this checklist to verify all agentic requirements:

### Core Requirements
- [ ] **Single Agent**: One agent makes all decisions (not multi-agent)
- [ ] **Chat Control**: All interaction through conversation
- [ ] **Dynamic Selection**: Agent chooses actions at runtime
- [ ] **Step Reordering**: Can skip/revisit steps freely
- [ ] **No Hard-coded Flow**: No if/then workflow logic

### State Management
- [ ] **Certificate State**: Tracks extracted fields and confidence
- [ ] **Evaluation State**: Manages criteria, weights, scores
- [ ] **Conversation State**: Maintains full dialogue history
- [ ] **Persistent Context**: State accumulates across turns
- [ ] **No Resets**: Corrections update state, don't restart

### Explainability
- [ ] **Reasoning Visible**: Agent explains why it chose each action
- [ ] **Uncertainty Flagged**: Low confidence data is identified
- [ ] **Decision Trail**: Can trace reasoning through history
- [ ] **Justification**: Agent can explain scores and assessments

### User Control
- [ ] **Interventions Work**: User can correct agent mid-flow
- [ ] **Criteria Changeable**: Evaluation parameters modifiable anytime
- [ ] **Re-evaluation**: Can re-score without re-extracting
- [ ] **Challenges Accepted**: Agent updates when user disputes

---

## Common Issues and Debugging

### Issue: Agent always chooses same action
**Cause**: LLM not receiving full context
**Fix**: Check that state is passed correctly to agent_node

### Issue: State resets between turns
**Cause**: Graph not persisting state properly
**Fix**: Verify `state = graph.invoke(state)` returns updated state

### Issue: JSON parsing errors
**Cause**: LLM returning non-JSON response
**Fix**: Use safe_json_parse utility (already implemented)

### Issue: No conversation history
**Cause**: Actions not appending to conversation_history
**Fix**: Check all actions call `append()` on history list

---

## Performance Validation

### Response Time
- Each turn should complete in < 5 seconds (depends on Gemini API)
- History retrieval should be instant (in-memory)

### Memory Usage
- Conversation history grows with turns
- For 100 turns, expect ~1-2MB memory usage

### Accuracy
- Extraction confidence should be > 85% for structured certificates
- Scoring should be mathematically correct based on weights

---

## Expected Output Examples

### Good Extraction Output:
```
✓ Extracted certificate information:
- Name: Sarah Chen
- Degree: Bachelor of Science in Computer Science
- GPA: 3.87

Confidence levels:
- Name: 98.5%
- Degree: 97.2%
- GPA: 95.3%
```

### Good Scoring Output:
```
✓ Certificate re-scored based on current criteria:

- Academic Performance: 154.8 (weight: 0.4)
- Research Experience: 38.0 (weight: 0.4)
- Leadership: 18.4 (weight: 0.2)

**Final Weighted Score: 92.7/100**
```

### Good Explanation Output:
```
**Decision Explanation:**

**Reason for last step:** User requested scoring after criteria modification
**Uncertainty:** None identified
**Extracted Data:** [list of fields with confidence]
**Current Score:** 92.7/100
**Active Criteria:** [list with weights]
```

---

## Integration Testing

### End-to-End Test Script
Run this complete dialogue to test all features:

```python
# Test script (paste in Python REPL or file)
test_inputs = [
    "Extract my certificate information",
    "I think the GPA should be higher",
    "Set criteria: GPA 40%, Institution 30%, Research 30%",
    "Score my certificate",
    "Change GPA weight to 50%",
    "Re-score",
    "Explain why the score changed",
    "history",
]

# Run through each input and verify responses
```

---

## Success Criteria

The system passes testing if:

1. ✅ **All 8 core tests pass** without errors
2. ✅ **State persists** across all turns
3. ✅ **No crashes** on valid inputs
4. ✅ **Reasoning is clear** and accessible
5. ✅ **Non-linear flows work** (step reordering)
6. ✅ **Corrections are applied** without restart
7. ✅ **History is maintained** and retrievable
8. ✅ **Criteria changes** trigger re-evaluation

---

## Troubleshooting

### If tests fail:
1. Check `conversation_history` is populated
2. Verify `reasoning_history` records decisions
3. Ensure `criteria` dict updates correctly
4. Confirm `extracted_fields` persist across corrections
5. Validate JSON parsing doesn't fail silently

### Debug mode:
Uncomment reasoning display in `main.py` to see decision-making process:
```python
# Shows reasoning for every turn (not just first 3)
print(f"\n💭 [Reasoning: {state.conversation.last_reason}]")
```

---

## Conclusion

This testing guide validates that the system is truly **agentic**:
- Not a workflow engine
- Not a rule-based chatbot
- Not a fixed pipeline

It's an **intelligent agent** that reasons about context and makes dynamic decisions at runtime.

Happy testing! 🎓🤖