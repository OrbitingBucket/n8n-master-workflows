# n8n Core Nodes Knowledge Base

**Version:** 1.0
**Last Updated:** 2025-11-09
**Analysis Source:** 100+ production workflows

## Quick Navigation

- [Tier 1: Core Nodes](#tier-1-core-nodes) - HTTP Request, Code, Split In Batches, IF, Schedule Trigger
- [Tier 2: High-Value Nodes](#tier-2-high-value-nodes) - Compare Datasets, Remove Duplicates, Merge, Error Trigger, Set
- [Tier 3: Advanced Nodes](#tier-3-advanced-nodes) - Aggregate, Execute Workflow, Limit, Filter, DateTime

---

# Tier 1: Core Nodes

## HTTP Request Node

**Type:** `n8n-nodes-base.httpRequest`
**Current Version:** 4.2

### Basic Structure
```json
{
  "name": "HTTP Request",
  "type": "n8n-nodes-base.httpRequest",
  "typeVersion": 4.2,
  "parameters": {
    "url": "https://api.example.com/endpoint",
    "method": "GET",
    "authentication": "none"
  }
}
```

### Request Methods
- GET, POST, PUT, DELETE, PATCH

### Authentication Types

**No Auth:**
```json
{"authentication": "none"}
```

**Header Auth:**
```json
{
  "sendHeaders": true,
  "headerParameters": {
    "parameters": [
      {"name": "Authorization", "value": "Bearer TOKEN"},
      {"name": "Content-Type", "value": "application/json"}
    ]
  }
}
```

**Basic Auth:**
```json
{
  "authentication": "genericCredentialType",
  "genericAuthType": "httpBasicAuth",
  "credentials": {
    "httpBasicAuth": {"id": "cred-id", "name": "Cred Name"}
  }
}
```

### Body Types

**JSON:**
```json
{
  "sendBody": true,
  "specifyBody": "json",
  "jsonBody": "={\"name\": \"{{ $json.name }}\"}"
}
```

**Form Data:**
```json
{
  "sendBody": true,
  "contentType": "form-urlencoded",
  "bodyParameters": {
    "parameters": [
      {"name": "field1", "value": "={{ $json.value }}"}
    ]
  }
}
```

### Query Parameters
```json
{
  "sendQuery": true,
  "queryParameters": {
    "parameters": [
      {"name": "page", "value": "1"},
      {"name": "limit", "value": "100"}
    ]
  }
}
```

### Error Handling
```json
{
  "onError": "continueRegularOutput",
  "retryOnFail": true,
  "maxTries": 3,
  "waitBetweenTries": 600
}
```

---

## Code Node

**Type:** `n8n-nodes-base.code`
**Current Version:** 2

### Basic Structure
```json
{
  "name": "Code",
  "type": "n8n-nodes-base.code",
  "typeVersion": 2,
  "parameters": {
    "mode": "runOnceForEachItem",
    "language": "javaScript",
    "jsCode": "return items;"
  }
}
```

### Execution Modes
- `runOnceForAllItems` - Process all items together
- `runOnceForEachItem` - Process items individually

### Accessing Data

**Current Item:**
```javascript
const data = $json;
const field = $json.fieldName;
```

**All Items:**
```javascript
const items = $input.all();
const first = $input.first();
```

**Other Nodes:**
```javascript
const nodeData = $('Node Name').item.json;
const allData = $('Node Name').all();
```

### Common Patterns

**Filter Items:**
```javascript
const filtered = $input.all().filter(item => {
  return item.json.score > 50;
});
return filtered;
```

**Transform Data:**
```javascript
return items.map(item => ({
  json: {
    ...item.json,
    processed: true,
    timestamp: new Date().toISOString()
  }
}));
```

**Workflow Static Data (Persistence):**
```javascript
// Get stored data
const stored = $getWorkflowStaticData('global')['myKey'] || null;

// Store data
$getWorkflowStaticData('global')['myKey'] = {
  data: currentData,
  timestamp: new Date().toISOString()
};
```

**Return Single Item:**
```javascript
return [{
  json: {
    message: "Success",
    count: items.length
  }
}];
```

---

## Split In Batches Node

**Type:** `n8n-nodes-base.splitInBatches`
**Current Version:** 3

### Basic Structure
```json
{
  "name": "Split In Batches",
  "type": "n8n-nodes-base.splitInBatches",
  "typeVersion": 3,
  "parameters": {
    "batchSize": 10,
    "options": {"reset": false}
  }
}
```

### Connection Pattern
**Two Outputs:**
- Output 0 (top): All batches complete
- Output 1 (bottom): Each batch (loop back here)

```json
"connections": {
  "Split In Batches": {
    "main": [
      [{"node": "Final Node", "type": "main", "index": 0}],
      [{"node": "Process Batch", "type": "main", "index": 0}]
    ]
  },
  "Process Batch": {
    "main": [[{"node": "Split In Batches", "type": "main", "index": 0}]]
  }
}
```

### Common Pattern
```
Data Source → Split In Batches → Process Batch → Wait → Loop Back
                      ↓
                 All Complete
```

---

## IF Node

**Type:** `n8n-nodes-base.if`
**Current Version:** 2.2

### Basic Structure
```json
{
  "name": "IF",
  "type": "n8n-nodes-base.if",
  "typeVersion": 2.2,
  "parameters": {
    "conditions": {
      "combinator": "and",
      "conditions": [
        {
          "operator": {"type": "string", "operation": "equals"},
          "leftValue": "={{ $json.status }}",
          "rightValue": "active"
        }
      ]
    }
  }
}
```

### Condition Types

**String:**
```json
{
  "operator": {"type": "string", "operation": "equals"},
  "leftValue": "={{ $json.field }}",
  "rightValue": "value"
}
```
Operations: equals, notEquals, contains, notContains, startsWith, endsWith, regex

**Number:**
```json
{
  "operator": {"type": "number", "operation": "larger"},
  "leftValue": "={{ $json.count }}",
  "rightValue": "10"
}
```
Operations: larger, smaller, equal, notEqual, largerEqual, smallerEqual

**Boolean:**
```json
{
  "operator": {"type": "boolean", "operation": "true"},
  "leftValue": "={{ $json.isActive }}"
}
```

**DateTime:**
```json
{
  "operator": {"type": "dateTime", "operation": "after"},
  "leftValue": "={{ $json.date }}",
  "rightValue": "2025-01-01"
}
```

### Multiple Conditions

**AND:**
```json
{"combinator": "and", "conditions": [...]}
```

**OR:**
```json
{"combinator": "or", "conditions": [...]}
```

### Connection Structure
**Two Outputs:**
- Output 0: True path
- Output 1: False path

---

## Schedule Trigger Node

**Type:** `n8n-nodes-base.scheduleTrigger`
**Current Version:** 1.2

### Basic Structure
```json
{
  "name": "Schedule Trigger",
  "type": "n8n-nodes-base.scheduleTrigger",
  "typeVersion": 1.2,
  "parameters": {
    "rule": {"interval": [{}]}
  }
}
```

### Interval Types

**Every Minute:**
```json
{
  "rule": {
    "interval": [
      {"field": "minutes", "minutesInterval": 1}
    ]
  }
}
```

**Every Hour:**
```json
{
  "rule": {
    "interval": [
      {"field": "hours", "hoursInterval": 1}
    ]
  }
}
```

**Every Day:**
```json
{
  "rule": {"interval": [{}]}
}
```

**Weekly (Monday 9 AM):**
```json
{
  "rule": {
    "interval": [
      {
        "field": "weeks",
        "triggerAtDay": [1],
        "triggerAtHour": 9
      }
    ]
  }
}
```

### Cron Expressions

**Daily at 9 AM:**
```json
{
  "rule": {
    "interval": [
      {"field": "cronExpression", "expression": "0 9 * * *"}
    ]
  }
}
```

**Every Hour:**
```json
{"expression": "0 * * * *"}
```

**Every Monday at 9 AM:**
```json
{"expression": "0 9 * * 1"}
```

---

# Tier 2: High-Value Nodes

## Compare Datasets Node

**Type:** `n8n-nodes-base.compareDatasets`
**Current Version:** 2.3
**Inputs:** 2
**Outputs:** 4

### Basic Structure
```json
{
  "name": "Compare Datasets",
  "type": "n8n-nodes-base.compareDatasets",
  "typeVersion": 2.3,
  "parameters": {
    "mergeByFields": {
      "values": [
        {"field1": "email", "field2": "email"}
      ]
    }
  }
}
```

### Output Branches
1. **Output 0:** Only in Input 1
2. **Output 1:** Same in Both
3. **Output 2:** Different in Both
4. **Output 3:** Only in Input 2

### Multiple Matching Fields
```json
{
  "mergeByFields": {
    "values": [
      {"field1": "customerNumber", "field2": "customerNumber"},
      {"field1": "year", "field2": "year"}
    ]
  }
}
```

### Options
```json
{
  "resolve": "preferInput1",  // preferInput1, preferInput2, includeBoth
  "options": {
    "skipFields": "field1,field2,field3"
  }
}
```

### Common Pattern - Two-Way Sync
```json
"connections": {
  "Compare Datasets": {
    "main": [
      [{"node": "Create in System 1", "type": "main", "index": 0}],
      [],
      [{"node": "Update Records", "type": "main", "index": 0}],
      [{"node": "Create in System 2", "type": "main", "index": 0}]
    ]
  }
}
```

---

## Remove Duplicates Node

**Type:** `n8n-nodes-base.removeDuplicates`
**Current Version:** 1.1 / 2

### Basic Structure
```json
{
  "name": "Remove Duplicates",
  "type": "n8n-nodes-base.removeDuplicates",
  "typeVersion": 1.1,
  "parameters": {
    "compare": "selectedFields",
    "fieldsToCompare": "email"
  }
}
```

### Compare Modes

**All Fields:**
```json
{"compare": "allFields"}
```

**Selected Fields:**
```json
{
  "compare": "selectedFields",
  "fieldsToCompare": "email,phone"
}
```

**Nested Fields:**
```json
{"fieldsToCompare": "user.email,user.id"}
```

---

## Merge Node

**Type:** `n8n-nodes-base.merge`
**Current Version:** 3.2
**Inputs:** 2+

### Merge Modes

**1. Append (Combine All):**
```json
{
  "name": "Merge",
  "type": "n8n-nodes-base.merge",
  "typeVersion": 3.2,
  "parameters": {"mode": "append"}
}
```

**2. Combine By Position:**
```json
{
  "parameters": {
    "mode": "combine",
    "combineBy": "combineByPosition",
    "numberInputs": 4,
    "options": {"includeUnpaired": true}
  }
}
```

**3. Merge By Key:**
```json
{
  "parameters": {
    "mode": "mergeByKey",
    "propertyName1": "requester_id",
    "propertyName2": "id"
  },
  "typeVersion": 1
}
```

### Data Enrichment Pattern
```
Get Records → Merge (input 0)
                ↑
Get Details ────┘ (input 1)
```

---

## Error Trigger Node

**Type:** `n8n-nodes-base.errorTrigger`
**Current Version:** 1
**Inputs:** 0 (trigger)

### Basic Structure
```json
{
  "name": "Error Trigger",
  "type": "n8n-nodes-base.errorTrigger",
  "typeVersion": 1,
  "parameters": {}
}
```

### Error Data Structure
```json
{
  "workflow": {
    "id": "workflow-id",
    "name": "My Workflow"
  },
  "execution": {
    "id": 123,
    "url": "https://n8n.example.com/execution/123",
    "mode": "manual",
    "error": {
      "message": "Error message",
      "stack": "Stack trace...",
      "timestamp": 1748605421337
    },
    "lastNodeExecuted": "Node Name"
  }
}
```

### Common Pattern - Notification
```
Error Trigger → Format Message → Send Notification (Telegram/Slack/Email)
```

### Accessing Error Data
```javascript
{{ $('Error Trigger').first().json.workflow.name }}
{{ $('Error Trigger').first().json.execution.url }}
{{ $('Error Trigger').first().json.execution.lastNodeExecuted }}
{{ $('Error Trigger').first().json.execution.error.message }}
```

---

## Set Node

**Type:** `n8n-nodes-base.set`
**Current Version:** 3.4 (Recommended)

### Basic Structure (v3.4)
```json
{
  "name": "Set",
  "type": "n8n-nodes-base.set",
  "typeVersion": 3.4,
  "parameters": {
    "assignments": {
      "assignments": [
        {
          "id": "unique-id",
          "name": "fieldName",
          "type": "string",
          "value": "fieldValue"
        }
      ]
    },
    "includeOtherFields": true
  }
}
```

### Assignment Types

**String:**
```json
{
  "id": "1",
  "name": "email",
  "type": "string",
  "value": "={{ $json.email }}"
}
```

**Number:**
```json
{
  "id": "2",
  "name": "count",
  "type": "number",
  "value": "={{ $json.count }}"
}
```

**Boolean:**
```json
{
  "id": "3",
  "name": "isActive",
  "type": "boolean",
  "value": true
}
```

**Array:**
```json
{
  "id": "4",
  "name": "items",
  "type": "array",
  "value": "={{ $json.items }}"
}
```

**Object:**
```json
{
  "id": "5",
  "name": "metadata",
  "type": "object",
  "value": "={{ $json.meta }}"
}
```

### includeOtherFields
- `true`: Keep existing fields, add new ones
- `false`: Only include assigned fields

---

# Tier 3: Advanced Nodes

## Aggregate Node

**Type:** `n8n-nodes-base.aggregate`
**Current Version:** 1

### Basic Structure
```json
{
  "name": "Aggregate",
  "type": "n8n-nodes-base.aggregate",
  "typeVersion": 1,
  "parameters": {
    "fieldsToAggregate": {
      "fieldToAggregate": [
        {"fieldToAggregate": "email"},
        {"fieldToAggregate": "name"}
      ]
    }
  }
}
```

### Input → Output
**Input (3 items):**
```json
[
  {"name": "John", "email": "john@example.com"},
  {"name": "Jane", "email": "jane@example.com"},
  {"name": "Bob", "email": "bob@example.com"}
]
```

**Output (1 item):**
```json
{
  "name": ["John", "Jane", "Bob"],
  "email": ["john@example.com", "jane@example.com", "bob@example.com"]
}
```

### Merge Lists Option
```json
{
  "parameters": {
    "options": {"mergeLists": true},
    "fieldsToAggregate": {
      "fieldToAggregate": [{"fieldToAggregate": "emails"}]
    }
  }
}
```

**Use Case:** Prevents nested arrays when aggregating array fields

---

## Execute Workflow Node

**Type:** `n8n-nodes-base.executeWorkflow`
**Current Version:** 1.1

### Basic Structure
```json
{
  "name": "Execute Workflow",
  "type": "n8n-nodes-base.executeWorkflow",
  "typeVersion": 1.1,
  "parameters": {
    "workflowId": {
      "__rl": true,
      "mode": "list",
      "value": "workflow-id-here",
      "cachedResultName": "Sub Workflow Name"
    }
  }
}
```

### Execution Modes

**Run Once:**
```json
{"mode": "once"}
```

**Run for Each Item:**
```json
{"mode": "each"}
```

**Fire and Forget:**
```json
{
  "mode": "each",
  "options": {"waitForSubWorkflow": false}
}
```

### Execute Current Workflow (Recursive)
```json
{
  "workflowId": {
    "__rl": true,
    "mode": "id",
    "value": "={{ $workflow.id }}"
  }
}
```

---

## Limit Node

**Type:** `n8n-nodes-base.limit`
**Current Version:** 1

### Basic Structure
```json
{
  "name": "Limit",
  "type": "n8n-nodes-base.limit",
  "typeVersion": 1,
  "parameters": {
    "maxItems": 10,
    "keep": "firstItems"
  }
}
```

### Keep Options
- `firstItems` (default)
- `lastItems`

### Common Use Cases
- Testing workflows with limited data
- Top N results after sorting
- Preview mode

---

## Filter Node

**Type:** `n8n-nodes-base.filter`
**Current Version:** 2.2

### Basic Structure
```json
{
  "name": "Filter",
  "type": "n8n-nodes-base.filter",
  "typeVersion": 2.2,
  "parameters": {
    "conditions": {
      "combinator": "and",
      "conditions": [
        {
          "operator": {"type": "string", "operation": "contains"},
          "leftValue": "={{ $json.email }}",
          "rightValue": "@company.com"
        }
      ]
    }
  }
}
```

### Common Operations

**String:**
- equals, notEquals, contains, notContains, startsWith, endsWith, regex, notRegex, isEmpty, isNotEmpty

**Number:**
- equal, notEqual, gt, lt, gte, lte

**Boolean:**
- true, false

**Array:**
- empty, notEmpty

### Filter vs IF Node
- **Filter:** Removes items that don't match (1 output)
- **IF:** Routes items to different paths (2 outputs)

---

## DateTime Node

**Type:** `n8n-nodes-base.dateTime`
**Current Version:** 2

### Basic Structure
```json
{
  "name": "Date & Time",
  "type": "n8n-nodes-base.dateTime",
  "typeVersion": 2,
  "parameters": {
    "value": "={{ $now }}",
    "toFormat": "yyyy-MM-dd"
  }
}
```

### Format Patterns
```
"yyyy-MM-dd"           // 2025-01-15
"yyyy-MM-dd HH:mm:ss"  // 2025-01-15 14:30:00
"MMMM DD YYYY"         // January 15 2025
"HH:mm:ss"             // 14:30:00
```

### Calculate/Add Time
```json
{
  "parameters": {
    "value": "={{ $now }}",
    "action": "calculate",
    "operation": "add",
    "duration": 7,
    "timeUnit": "days"
  }
}
```

**Time Units:** seconds, minutes, hours, days, weeks, months, years

### Date Expressions
```javascript
// Current timestamp
{{ $now }}

// Today at midnight
{{ $today }}

// Add time
{{ $now.plus({days: 7}) }}

// Subtract time
{{ $now.minus({hours: 1}) }}

// Format
{{ $now.toFormat('yyyy-MM-dd') }}

// Check weekend
{{ $now.isWeekend() }}

// Beginning of month
{{ $now.startOf('month') }}
```

---

# Quick Reference Tables

## Node Selection Guide

| Need | Use Node | Alternative |
|------|----------|-------------|
| API call | HTTP Request | - |
| Custom logic | Code | - |
| Process in batches | Split In Batches | - |
| Branch workflow | IF | Switch |
| Schedule execution | Schedule Trigger | Cron Trigger |
| Find changes | Compare Datasets | Code |
| Remove duplicates | Remove Duplicates | Code + Filter |
| Combine data | Merge | Code |
| Handle errors | Error Trigger | - |
| Transform fields | Set | Code |
| Consolidate items | Aggregate | Code |
| Call sub-workflow | Execute Workflow | - |
| Limit results | Limit | Code |
| Remove items | Filter | IF |
| Date operations | DateTime | Code |

## Common Workflow Patterns

### API Integration
```
Schedule → Code (prepare) → HTTP Request → Filter → Set → Database
```

### Batch Processing
```
Database → Split In Batches → HTTP Request → Wait → Loop Back
              ↓
         All Complete
```

### Data Synchronization
```
System A → Compare Datasets → Create (output 0)
System B ↗                   → Update (output 2)
                             → Delete (output 3)
```

### Error Handling
```
[Any Workflow] → Error Trigger → Format → Notification
```

### ETL Pipeline
```
Extract → Filter → Remove Duplicates → Set → Aggregate → Load
```

---

# Best Practices

## General
- Use latest typeVersion for all nodes
- Test with Limit node before full runs
- Add sticky notes for complex logic
- Use descriptive node names
- Handle errors appropriately

## Performance
- Filter early in workflows
- Use batch processing for large datasets
- Implement retry logic for API calls
- Aggregate before sub-workflows
- Remove duplicates early

## Maintainability
- Break complex workflows into sub-workflows
- Use Set node for configuration variables
- Document error handling strategies
- Use consistent naming conventions
- Version control workflow JSON

## Security
- Store credentials in n8n credential system
- Never hardcode API keys
- Use environment variables
- Implement proper error handling
- Log errors securely

---

**End of Knowledge Base**
