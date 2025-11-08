# Remediation Quick Start Guide

## How to Use Remediation Cards

Each card in `remediation_cards.jsonl` provides a complete roadmap for fixing quality issues in a workflow.

### 1. Find Workflows to Fix

**High Priority First (227 workflows):**
```bash
grep '"priority":"high"' remediation_cards.jsonl | head -n 10
```

**Filter by Specific Issue:**
```bash
# Find all blind-update issues
grep 'blind-update' remediation_cards.jsonl

# Find all missing-pagination issues
grep 'missing-pagination' remediation_cards.jsonl
```

### 2. Read a Remediation Card

**Pretty Print a Card:**
```bash
# View first high-priority card
grep '"priority":"high"' remediation_cards.jsonl | head -n 1 | python3 -m json.tool
```

**Card Structure:**
```json
{
  "filePath": "./path/to/workflow.json",
  "priority": "high",
  "reasons": ["blind-update", "missing-typecast"],
  "fixPlan": [...],      // Step-by-step instructions
  "n8nPatches": [...],   // Automated JSON patches
  "tests": [...],        // Verification criteria
  "estimatedImpact": {   // Expected improvements
    "reliability": "+15",
    "maintainability": "+5",
    "security": "+0"
  }
}
```

### 3. Apply Fixes Manually

#### Example: Fix "blind-update" Issue

**Problem:** Workflow updates Airtable records without checking if they exist

**Fix Plan:**
```json
[
  {
    "step": "insert",
    "node": "Airtable",
    "operation": "search",
    "where": "before:update",
    "params": {"filterByFormula": "RECORD_ID()='{{$json.id}}'"}
  },
  {
    "step": "branch",
    "type": "if",
    "condition": "{{ $json.records.length > 0 }}",
    "then": "update",
    "else": "create"
  }
]
```

**Manual Steps:**
1. Open workflow in n8n
2. Before the "Update" node, add new "Airtable" node
3. Set operation to "Search"
4. Set filterByFormula: `RECORD_ID()='{{$json.id}}'`
5. Add "IF" node after Search
6. Condition: `{{ $json.records.length > 0 }}`
7. Connect IF true → Update, false → Create

#### Example: Fix "missing-pagination" Issue

**Problem:** List operation fetches all records at once, causing rate limits

**Fix Plan:**
```json
[
  {
    "step": "insert",
    "node": "SplitInBatches",
    "size": 50,
    "where": "before:airtable.list"
  },
  {
    "step": "insert",
    "node": "Wait",
    "ms": 150,
    "where": "after:splitInBatches.loop"
  }
]
```

**Manual Steps:**
1. Before Airtable List node, add "SplitInBatches"
2. Set batch size: 50
3. After processing loop, add "Wait" node
4. Set wait time: 150ms
5. Connect back to SplitInBatches for next batch

#### Example: Fix "missing-typecast" Issue

**Problem:** Number/date fields reject string inputs

**Fix Plan:**
```json
[
  {
    "step": "setOption",
    "node": "Airtable(operation=create|update)",
    "option": "options.typecast",
    "value": true
  }
]
```

**Manual Steps:**
1. Open Airtable Create or Update node
2. Click "Add Option"
3. Select "Typecast"
4. Enable the toggle

### 4. Apply Fixes Programmatically

Use the `n8nPatches` array to automate fixes:

```python
import json

def apply_remediation(workflow_path, patches):
    """Apply JSON patches to workflow."""
    with open(workflow_path, 'r') as f:
        workflow = json.load(f)

    for patch in patches:
        if patch['op'] == 'add':
            # Add new node
            if patch['path'] == '/nodes/-':
                workflow['nodes'].append(patch['value'])
        elif patch['op'] == 'replace':
            # Update existing value
            # Parse path and update
            pass

    with open(workflow_path, 'w') as f:
        json.dump(workflow, f, indent=2)
```

### 5. Verify Fixes

Use the `tests` array as acceptance criteria:

```json
"tests": [
  "Given duplicate email, Update executes and Create is skipped",
  "Given new email, Create executes and Update is skipped",
  "List 500 records completes with batches and no 429 error"
]
```

**Verification Checklist:**
- [ ] Open workflow in n8n editor
- [ ] Execute with test data
- [ ] Verify each test case passes
- [ ] Check execution logs for errors
- [ ] Confirm no rate limit (429) errors

### 6. Measure Impact

**Before Fixes:**
```json
"qualityNotes": {
  "scores": {
    "reliability": 50,
    "maintainability": 60
  }
}
```

**Estimated After Fixes:**
```json
"estimatedImpact": {
  "reliability": "+25",  // 50 + 25 = 75
  "maintainability": "+5" // 60 + 5 = 65
}
```

**Re-run Quality Analysis:**
```bash
# After fixing, regenerate workflow cards
python3 analyze_workflows.py

# Compare scores
diff old_scores.json new_scores.json
```

## Common Fix Patterns

### Pattern 1: Search Before Modify (Upsert Pattern)

**When:** `blind-update` or `no-dedupe-before-create`

**Nodes to Add:**
1. Airtable Search (with filterByFormula)
2. IF node (check if records found)
3. Branch to Update or Create

### Pattern 2: Batch Processing

**When:** `missing-pagination`

**Nodes to Add:**
1. SplitInBatches (size: 50)
2. Wait (150ms between batches)
3. Set limit on Airtable List (100)

### Pattern 3: Enable Safety Options

**When:** `missing-typecast` or `low-reliability`

**Options to Enable:**
- Typecast (on Create/Update)
- Retry on Fail (all nodes)
- Max Tries: 3

## Workflow Improvement Workflow

1. **Identify** → Review remediation_cards.jsonl
2. **Prioritize** → Start with "high" priority
3. **Fix** → Follow fixPlan steps
4. **Test** → Verify with test cases
5. **Measure** → Compare before/after scores
6. **Document** → Update workflow notes

## Getting Help

**View Specific Card:**
```bash
# By filename
grep "Auto-Create_Podcast" remediation_cards.jsonl | python3 -m json.tool

# By issue type
grep "blind-update" remediation_cards.jsonl | python3 -m json.tool | less
```

**Count Issues:**
```bash
# Total cards needing pagination fixes
grep "missing-pagination" remediation_cards.jsonl | wc -l

# Total high-priority cards
grep '"priority":"high"' remediation_cards.jsonl | wc -l
```

**Statistics:**
```python
python3 -c "
import json
from collections import Counter

with open('remediation_cards.jsonl') as f:
    cards = [json.loads(line) for line in f if line.strip()]

print(f'Total workflows needing fixes: {len(cards)}')
print(f'Total fix steps: {sum(len(c[\"fixPlan\"]) for c in cards)}')
print(f'Avg steps per workflow: {sum(len(c[\"fixPlan\"]) for c in cards) / len(cards):.1f}')
"
```

---

**Pro Tip:** Focus on fixing `blind-update` and `no-dedupe-before-create` issues first. These have the highest risk of data corruption and corruption prevention yields the biggest reliability improvements.
