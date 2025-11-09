# n8n Airtable Node Knowledge Base

**Version:** 1.0
**Last Updated:** 2025-11-09
**Purpose:** Technical reference for AI agents building n8n workflows with Airtable nodes
**Source:** Analysis of 100+ production n8n workflows

---

## Table of Contents

1. [Node Type Overview](#1-node-type-overview)
2. [Authentication and Credentials](#2-authentication-and-credentials)
3. [Node Structure Reference](#3-node-structure-reference)
4. [Operation Types](#4-operation-types)
5. [Field Mapping Patterns](#5-field-mapping-patterns)
6. [Data Type Handling](#6-data-type-handling)
7. [Expression Syntax](#7-expression-syntax)
8. [Workflow Architecture Patterns](#8-workflow-architecture-patterns)
9. [Connection Structures](#9-connection-structures)
10. [Common Use Cases](#10-common-use-cases)
11. [Best Practices](#11-best-practices)

---

## 1. Node Type Overview

### Primary Node Types

| Node Type | Purpose | Current Version |
|-----------|---------|-----------------|
| `n8n-nodes-base.airtable` | Main Airtable operations (CRUD) | 2.1 |
| `n8n-nodes-base.airtableTrigger` | Poll Airtable for changes | 1.0 |

### Version History

- **TypeVersion 1**: Legacy, uses API key authentication
- **TypeVersion 2.1**: Current, uses Personal Access Token (PAT)

**Migration Note:** Always use TypeVersion 2.1 for new workflows.

---

## 2. Authentication and Credentials

### Legacy Authentication (TypeVersion 1)

```json
{
  "credentials": {
    "airtableApi": "Airtable Credentials n8n"
  },
  "typeVersion": 1
}
```

**Characteristics:**
- Simple string reference
- Full account access
- Deprecated for new workflows

### Modern Authentication (TypeVersion 2.1) ⭐ RECOMMENDED

```json
{
  "credentials": {
    "airtableTokenApi": {
      "id": "WKxw33bpSEDiQEaU",
      "name": "Airtable Personal Access Token account"
    }
  },
  "typeVersion": 2.1
}
```

**Required Scopes:**
- `data.records:read`
- `data.records:write`
- `schema.bases:read`

**Setup URL:** `https://airtable.com/create/tokens/new`

---

## 3. Node Structure Reference

### Complete Node Anatomy

```json
{
  "id": "unique-node-id",
  "name": "Descriptive Node Name",
  "type": "n8n-nodes-base.airtable",
  "position": [900, 420],
  "typeVersion": 2.1,
  "parameters": {
    "base": { /* Base reference */ },
    "table": { /* Table reference */ },
    "operation": "create",
    "columns": { /* Field mappings */ },
    "options": { /* Additional options */ }
  },
  "credentials": {
    "airtableTokenApi": {
      "id": "credential-id",
      "name": "credential-name"
    }
  },
  "alwaysOutputData": false,
  "executeOnce": false
}
```

### Base and Table References

#### Resource Locator Object (TypeVersion 2.1)

**Mode: list** (Selected from dropdown)
```json
{
  "base": {
    "__rl": true,
    "mode": "list",
    "value": "appndgSF4faN4jPXi",
    "cachedResultUrl": "https://airtable.com/appndgSF4faN4jPXi",
    "cachedResultName": "Project Database"
  },
  "table": {
    "__rl": true,
    "mode": "list",
    "value": "tblaCSndQsSF3gq7Z",
    "cachedResultUrl": "https://airtable.com/appndgSF4faN4jPXi/tblaCSndQsSF3gq7Z",
    "cachedResultName": "Tasks"
  }
}
```

**Mode: id** (Dynamic/Expression-based)
```json
{
  "base": {
    "__rl": true,
    "mode": "id",
    "value": "={{ $json.baseId }}"
  }
}
```

**Mode: url** (By Airtable URL)
```json
{
  "base": {
    "__rl": true,
    "mode": "url",
    "value": "https://airtable.com/appKtypfMptBIKStp"
  }
}
```

---

## 4. Operation Types

### 4.1 CREATE Operation

Creates new records in Airtable.

#### Auto-Map Input (Simplest)

```json
{
  "operation": "create",
  "columns": {
    "mappingMode": "autoMapInputData",
    "matchingColumns": []
  }
}
```

**Use Case:** When input data exactly matches Airtable field names.

#### Manual Field Mapping (Most Common)

```json
{
  "operation": "create",
  "columns": {
    "value": {
      "Name": "={{ $json.name }}",
      "Email": "={{ $json.email }}",
      "Priority": "={{ $json.priority }}",
      "Due Date": "={{ $json.due_date }}",
      "Project": "={{ [$json.project_name] }}"
    },
    "schema": [
      {
        "id": "Name",
        "type": "string",
        "display": true,
        "required": false,
        "canBeUsedToMatch": true
      },
      {
        "id": "Priority",
        "type": "options",
        "options": [
          {"name": "Low", "value": "Low"},
          {"name": "Medium", "value": "Medium"},
          {"name": "Urgent", "value": "Urgent"}
        ]
      },
      {
        "id": "Due Date",
        "type": "dateTime"
      },
      {
        "id": "Project",
        "type": "array"
      }
    ],
    "mappingMode": "defineBelow",
    "matchingColumns": [],
    "attemptToConvertTypes": false,
    "convertFieldsToString": false
  },
  "options": {
    "typecast": true
  }
}
```

**Key Parameters:**
- `value`: Field name → Expression mapping
- `schema`: Field definitions with types
- `mappingMode`: `"defineBelow"` or `"autoMapInputData"`
- `options.typecast`: Auto-convert data types (recommended: `true`)

---

### 4.2 UPDATE Operation

Updates existing records by matching on specific fields.

```json
{
  "operation": "update",
  "columns": {
    "value": {
      "Count": "={{ $json.Count }}",
      "WhatsApp_ID": "={{ $json.from }}",
      "Last interaction": "={{ $now.format('yyyy.MM.dd') }}"
    },
    "schema": [
      {
        "id": "id",
        "type": "string",
        "readOnly": true,
        "defaultMatch": true
      },
      {
        "id": "WhatsApp_ID",
        "type": "string",
        "canBeUsedToMatch": true
      },
      {
        "id": "Count",
        "type": "number"
      }
    ],
    "mappingMode": "defineBelow",
    "matchingColumns": ["WhatsApp_ID"]
  }
}
```

**Critical:** `matchingColumns` array specifies which field(s) to match records on.

---

### 4.3 UPSERT Operation

Update if exists, create if doesn't exist.

```json
{
  "operation": "upsert",
  "columns": {
    "value": {
      "company_name": "={{ $json.company_name }}",
      "job_summary": "={{ $json.output.recap }}",
      "is_finance_job": "={{ $json.output.is_finance_job }}"
    },
    "mappingMode": "defineBelow",
    "matchingColumns": ["company_name"]
  }
}
```

**Use Case:** Prevents duplicates when you're not sure if record exists.

---

### 4.4 SEARCH Operation

Query Airtable using formulas.

#### Simple Field Match
```json
{
  "operation": "search",
  "filterByFormula": "={WhatsApp_ID} = '{{ $json.phoneNumber }}'"
}
```

#### Complex AND Condition
```json
{
  "operation": "search",
  "filterByFormula": "=AND(time < \"{{ $json.now }}\", time > \"{{ $json.yesterday }}\")"
}
```

#### Multiple Conditions
```json
{
  "operation": "search",
  "filterByFormula": "=AND(url != \"\", {title tag} = \"\", {meta desc} = \"\")",
  "limit": 10,
  "returnAll": false
}
```

#### Numeric Comparison
```json
{
  "operation": "search",
  "filterByFormula": "={Total Score} > 15"
}
```

**Tip:** Use `alwaysOutputData: true` to continue workflow even if no results found.

---

### 4.5 LIST Operation

Retrieve all records (with optional filtering).

```json
{
  "operation": "list",
  "options": {
    "fields": ["company_name", "email", "status"],
    "filterByFormula": "{Status} = 'Active'"
  },
  "returnAll": true
}
```

**Pagination:**
- `returnAll: true` - Get all records
- `returnAll: false` + `limit: 100` - Get specific number

---

### 4.6 APPEND Operation (Legacy - TypeVersion 1)

```json
{
  "operation": "append",
  "application": "appflT9EkWRGsSFM2",
  "table": "Table 1",
  "fields": ["deal_name", "deal_id", "deal_type"],
  "addAllFields": false
}
```

**Note:** Use `create` with TypeVersion 2.1 instead.

---

### 4.7 GET SCHEMA Operation

Retrieve base/table schema metadata.

```json
{
  "resource": "base",
  "operation": "getSchema",
  "base": {
    "__rl": true,
    "mode": "id",
    "value": "={{ $json.BaseId }}"
  }
}
```

---

## 5. Field Mapping Patterns

### 5.1 Mapping Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| `autoMapInputData` | Auto-map all input fields | Input matches Airtable schema exactly |
| `defineBelow` | Manual field mapping | Transform or rename fields |

### 5.2 Schema Field Properties

```json
{
  "id": "FieldName",
  "type": "string|number|boolean|dateTime|options|array",
  "display": true,
  "removed": false,
  "readOnly": false,
  "required": false,
  "defaultMatch": false,
  "canBeUsedToMatch": true,
  "displayName": "Field Name",
  "options": [
    {"name": "Option 1", "value": "option1"}
  ]
}
```

### 5.3 Field Type Examples

#### String Field
```json
{
  "id": "Name",
  "type": "string",
  "canBeUsedToMatch": true
}
```

#### Number Field
```json
{
  "id": "Price",
  "type": "number"
}
```

#### Boolean Field
```json
{
  "id": "IsActive",
  "type": "boolean"
}
```

#### DateTime Field
```json
{
  "id": "CreatedAt",
  "type": "dateTime"
}
```

#### Single Select Field
```json
{
  "id": "Status",
  "type": "options",
  "options": [
    {"name": "Active", "value": "Active"},
    {"name": "Inactive", "value": "Inactive"}
  ]
}
```

#### Array/Multi-Select Field
```json
{
  "id": "Tags",
  "type": "array"
}
```

#### Linked Records Field
```json
{
  "id": "Project",
  "type": "array"
}
```

**Note:** For linked records, wrap value in array: `"={{ [$json.project_id] }}"`

---

## 6. Data Type Handling

### 6.1 String Values

```json
{
  "Name": "={{ $json.name }}",
  "Description": "={{ $json.description }}",
  "Status": "Active"
}
```

### 6.2 Numeric Values

```json
{
  "Price": "={{ $json.price }}",
  "Quantity": "={{ $json.quantity }}",
  "Total": "={{ $json.price * $json.quantity }}"
}
```

### 6.3 Boolean Values

```json
{
  "IsActive": "={{ $json.active }}",
  "HasSubscription": "={{ $json.subscription === 'yes' }}"
}
```

### 6.4 DateTime Values

```json
{
  "CreatedAt": "={{ new Date().toISOString() }}",
  "UpdatedAt": "={{ $now }}",
  "FormattedDate": "={{ $now.format('yyyy.MM.dd') }}",
  "DueDate": "={{ $json.dueDate }}"
}
```

### 6.5 Array Values

#### Single Value to Array
```json
{
  "LinkedRecord": "={{ [$json.recordId] }}"
}
```

#### Multiple Values
```json
{
  "Tags": "={{ $json.tags }}"
}
```

### 6.6 Type Conversion

```json
{
  "NumericId": "={{ $json.id.toNumber() }}",
  "LowerCaseName": "={{ $json.name.toLowerCase() }}",
  "TrimmedValue": "={{ $json.value.trim() }}"
}
```

### 6.7 Options Configuration

```json
{
  "options": {
    "typecast": true,              // Auto-convert types
    "bulkSize": 10,                // Batch size
    "ignoreErrors": true           // Continue on errors
  }
}
```

---

## 7. Expression Syntax

### 7.1 Current Item Data

```javascript
={{ $json.fieldName }}
={{ $json.body.messages[0].from }}
={{ $json.properties.dealname.value }}
={{ $json['Field with Spaces'] }}
={{ $json['You have Subscription ?'] }}
```

### 7.2 Previous Node Reference

```javascript
={{ $('NodeName').item.json.fieldName }}
={{ $node["NodeName"].json.fieldName }}
={{ $('Filter Valid Companies').item.json.company_link }}
```

### 7.3 Built-in Functions

```javascript
// Date/Time
={{ $now }}
={{ $now.format('yyyy.MM.dd') }}
={{ new Date().toISOString() }}

// String Operations
={{ $json.name.toLowerCase() }}
={{ $json.name.toUpperCase() }}
={{ $json.value.trim() }}

// Numeric
={{ $json.id.toNumber() }}
={{ $json.price * $json.quantity }}
```

### 7.4 Conditional Logic

```javascript
={{ $json.status === 'active' ? 'Active' : 'Inactive' }}
={{ $json.count > 10 ? 'High' : 'Low' }}
```

### 7.5 String Templates

```javascript
="Deal: {{$json.deal_name}}"
="https://airtable.com/{{ $json.baseId }}/{{ $json.tableId }}/{{ $json.recordId }}"
```

### 7.6 Array/Object Access

```javascript
={{ $json.items[0].name }}
={{ $json.user.address.city }}
={{ $json.data?.optional?.field }}  // Optional chaining
```

### 7.7 Complex Transformations

```javascript
={{ JSON.stringify($json.data) }}
={{ Object.keys($json.fields).length }}
={{ $json.tags.join(', ') }}
```

---

## 8. Workflow Architecture Patterns

### Pattern A: Form Submission → Airtable

**Use Case:** Store form data in Airtable

```
Webhook (Form Trigger)
  → Set (Transform Fields)
  → Airtable (Create)
  → Slack (Notification)
```

**Connection:**
```json
{
  "connections": {
    "Webhook": {
      "main": [[{"node": "Set", "type": "main", "index": 0}]]
    },
    "Set": {
      "main": [[{"node": "Airtable", "type": "main", "index": 0}]]
    },
    "Airtable": {
      "main": [[{"node": "Slack", "type": "main", "index": 0}]]
    }
  }
}
```

---

### Pattern B: Airtable Trigger → Action

**Use Case:** React to new Airtable records

```
Airtable Trigger (Poll for changes)
  → Filter (Check conditions)
  → Action Node (Send Email/Create Task)
```

**Trigger Configuration:**
```json
{
  "name": "Airtable Trigger",
  "type": "n8n-nodes-base.airtableTrigger",
  "parameters": {
    "pollTimes": {
      "item": [
        {
          "mode": "everyX",
          "unit": "minutes",
          "value": 10
        }
      ]
    },
    "triggerField": "Status",
    "additionalFields": {}
  }
}
```

---

### Pattern C: API → Transform → Airtable (ETL)

**Use Case:** Import data from external API

```
Schedule Trigger
  → HTTP Request (API)
  → Code (Transform)
  → Remove Duplicates
  → Airtable (Upsert)
```

**Deduplication:**
```json
{
  "name": "Remove Duplicates",
  "type": "n8n-nodes-base.removeDuplicates",
  "parameters": {
    "compare": "selectedFields",
    "fieldsToCompare": "email,company_name"
  }
}
```

---

### Pattern D: Airtable Search → Conditional Create/Update

**Use Case:** Check if record exists before creating

```
Webhook
  → Airtable (Search by Email)
  → If (Check if exists)
      → True: Airtable (Update)
      → False: Airtable (Create)
```

**If Node Configuration:**
```json
{
  "conditions": {
    "number": [
      {
        "value1": "={{ $json.length }}",
        "operation": "larger",
        "value2": 0
      }
    ]
  }
}
```

---

### Pattern E: Schedule → Airtable → Email Report

**Use Case:** Daily/weekly reports

```
Schedule Trigger
  → Code (Build date range)
  → Airtable (Search with formula)
  → HTML (Format report)
  → Email (Send)
```

**Schedule Configuration:**
```json
{
  "rule": {
    "interval": [
      {
        "field": "cronExpression",
        "expression": "0 9 * * *"
      }
    ]
  }
}
```

---

### Pattern F: AI Agent with Airtable Storage

**Use Case:** AI processes data and stores in Airtable

```
Webhook
  → AI Agent (with tools)
  → Extract Structured Data
  → Airtable (Create)
  → Response
```

**AI Tool Connection:**
```json
{
  "connections": {
    "AI Agent": {
      "ai_tool": [
        [{"node": "Airtable Tool", "type": "ai_tool", "index": 0}]
      ]
    }
  }
}
```

---

### Pattern G: Batch Processing with Loop

**Use Case:** Process Airtable records one by one

```
Manual Trigger
  → Airtable (List all)
  → Split in Batches (5 items)
  → Process Each Item
  → Airtable (Update)
  → Loop Back
```

**Split in Batches:**
```json
{
  "name": "Split in Batches",
  "type": "n8n-nodes-base.splitInBatches",
  "parameters": {
    "batchSize": 5,
    "options": {}
  }
}
```

---

### Pattern H: Multi-Platform Social Media with Airtable Tracking

**Use Case:** Post to social media and track in Airtable

```
Manual Trigger
  → AI (Generate Content)
  → Airtable (Create Draft)
  → Wait for Approval
  → Post to Instagram
  → Post to LinkedIn
  → Airtable (Update Status)
```

---

## 9. Connection Structures

### 9.1 Basic Connection

```json
{
  "connections": {
    "SourceNode": {
      "main": [
        [
          {
            "node": "TargetNode",
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
  }
}
```

### 9.2 Multiple Outputs (Switch/If Node)

```json
{
  "connections": {
    "Switch": {
      "main": [
        [{"node": "Path1Node", "type": "main", "index": 0}],
        [{"node": "Path2Node", "type": "main", "index": 0}],
        [{"node": "Path3Node", "type": "main", "index": 0}]
      ]
    }
  }
}
```

### 9.3 Multiple Targets (Parallel Processing)

```json
{
  "connections": {
    "SourceNode": {
      "main": [
        [
          {"node": "Target1", "type": "main", "index": 0},
          {"node": "Target2", "type": "main", "index": 0},
          {"node": "Target3", "type": "main", "index": 0}
        ]
      ]
    }
  }
}
```

### 9.4 AI Agent Connections

```json
{
  "connections": {
    "AI Agent": {
      "ai_tool": [
        [{"node": "Tool1", "type": "ai_tool", "index": 0}],
        [{"node": "Tool2", "type": "ai_tool", "index": 0}]
      ],
      "ai_languageModel": [
        [{"node": "OpenAI", "type": "ai_languageModel", "index": 0}]
      ],
      "ai_memory": [
        [{"node": "Memory", "type": "ai_memory", "index": 0}]
      ]
    }
  }
}
```

---

## 10. Common Use Cases

### 10.1 Store Form Submissions

```json
{
  "name": "Store Form Data",
  "type": "n8n-nodes-base.airtable",
  "typeVersion": 2.1,
  "parameters": {
    "base": {
      "__rl": true,
      "mode": "list",
      "value": "appXXXXXXXXXXXXXX"
    },
    "table": {
      "__rl": true,
      "mode": "list",
      "value": "tblXXXXXXXXXXXXXX"
    },
    "operation": "create",
    "columns": {
      "value": {
        "Name": "={{ $json.name }}",
        "Email": "={{ $json.email }}",
        "Message": "={{ $json.message }}",
        "Submitted At": "={{ $now }}"
      },
      "mappingMode": "defineBelow"
    },
    "options": {
      "typecast": true
    }
  },
  "credentials": {
    "airtableTokenApi": {
      "id": "credential-id",
      "name": "Airtable PAT"
    }
  }
}
```

---

### 10.2 Track User Engagement

```json
{
  "name": "Update User Count",
  "type": "n8n-nodes-base.airtable",
  "typeVersion": 2.1,
  "parameters": {
    "operation": "update",
    "columns": {
      "value": {
        "Count": "={{ $json.Count + 1 }}",
        "User_ID": "={{ $json.userId }}",
        "Last Interaction": "={{ $now.format('yyyy.MM.dd') }}"
      },
      "mappingMode": "defineBelow",
      "matchingColumns": ["User_ID"]
    }
  }
}
```

---

### 10.3 CRM Lead Storage

```json
{
  "name": "Save Lead",
  "type": "n8n-nodes-base.airtable",
  "typeVersion": 2.1,
  "parameters": {
    "operation": "upsert",
    "columns": {
      "value": {
        "email": "={{ $json.email }}",
        "first_name": "={{ $json.firstName }}",
        "last_name": "={{ $json.lastName }}",
        "company": "={{ $json.company }}",
        "linkedin_url": "={{ $json.linkedinUrl }}",
        "Status": "New Lead"
      },
      "schema": [
        {
          "id": "Status",
          "type": "options",
          "options": [
            {"name": "New Lead", "value": "New Lead"},
            {"name": "Contacted", "value": "Contacted"},
            {"name": "Qualified", "value": "Qualified"}
          ]
        }
      ],
      "mappingMode": "defineBelow",
      "matchingColumns": ["email"]
    },
    "options": {
      "typecast": true
    }
  }
}
```

---

### 10.4 Daily Weather Logging

```json
{
  "name": "Log Weather",
  "type": "n8n-nodes-base.airtable",
  "typeVersion": 2.1,
  "parameters": {
    "operation": "create",
    "columns": {
      "value": {
        "Date": "={{ $now }}",
        "Location": "={{ $json.name }}",
        "Temperature": "={{ $json.main.temp }}",
        "Humidity": "={{ $json.main.humidity }}",
        "Wind Speed": "={{ $json.wind.speed }}"
      },
      "schema": [
        {
          "id": "Temperature",
          "type": "number"
        },
        {
          "id": "Humidity",
          "type": "number"
        },
        {
          "id": "Wind Speed",
          "type": "number"
        }
      ],
      "mappingMode": "defineBelow"
    }
  }
}
```

---

### 10.5 File Metadata Tracking

```json
{
  "name": "Track Files",
  "type": "n8n-nodes-base.airtable",
  "typeVersion": 2.1,
  "parameters": {
    "operation": "create",
    "columns": {
      "value": {
        "File ID": "={{ $json.id }}",
        "File Name": "={{ $json.name }}",
        "Created Time": "={{ $json.createdTime }}",
        "Modified Time": "={{ $json.modifiedTime }}",
        "Size": "={{ $json.size }}"
      },
      "schema": [
        {
          "id": "Created Time",
          "type": "dateTime"
        },
        {
          "id": "Modified Time",
          "type": "dateTime"
        },
        {
          "id": "Size",
          "type": "number"
        }
      ],
      "mappingMode": "defineBelow"
    }
  }
}
```

---

### 10.6 Search and Filter Records

```json
{
  "name": "Find Active Users",
  "type": "n8n-nodes-base.airtable",
  "typeVersion": 2.1,
  "parameters": {
    "operation": "search",
    "filterByFormula": "=AND({Status} = 'Active', {Last Login} > '2025-01-01')",
    "options": {
      "fields": ["Name", "Email", "Status", "Last Login"]
    }
  },
  "alwaysOutputData": true
}
```

---

## 11. Best Practices

### ✅ DO

1. **Use TypeVersion 2.1** with Personal Access Tokens
   ```json
   {
     "typeVersion": 2.1,
     "credentials": {
       "airtableTokenApi": { "id": "...", "name": "..." }
     }
   }
   ```

2. **Enable typecast for automatic type conversion**
   ```json
   {
     "options": {
       "typecast": true
     }
   }
   ```

3. **Use upsert to prevent duplicates**
   ```json
   {
     "operation": "upsert",
     "columns": {
       "matchingColumns": ["email"]
     }
   }
   ```

4. **Define schema for complex field types**
   ```json
   {
     "schema": [
       {
         "id": "Status",
         "type": "options",
         "options": [{"name": "Active", "value": "Active"}]
       }
     ]
   }
   ```

5. **Use alwaysOutputData for search operations**
   ```json
   {
     "operation": "search",
     "alwaysOutputData": true
   }
   ```

6. **Wrap linked record IDs in arrays**
   ```json
   {
     "Project": "={{ [$json.projectId] }}"
   }
   ```

7. **Use Resource Locator mode appropriately**
   - `mode: "list"` for static selections
   - `mode: "id"` for dynamic/expression-based
   - `mode: "url"` for URL-based references

8. **Format dates properly**
   ```json
   {
     "Created At": "={{ $now }}",
     "Formatted Date": "={{ $now.format('yyyy.MM.dd') }}"
   }
   ```

---

### ❌ DON'T

1. **Don't use TypeVersion 1 for new workflows**
   - Deprecated authentication method
   - Less secure
   - Missing modern features

2. **Don't forget matchingColumns for update/upsert**
   ```json
   // WRONG
   {"operation": "update", "matchingColumns": []}

   // RIGHT
   {"operation": "update", "matchingColumns": ["email"]}
   ```

3. **Don't hardcode base/table IDs without resource locator**
   ```json
   // WRONG (v1 style)
   {"application": "appXXX", "table": "tblYYY"}

   // RIGHT (v2.1 style)
   {"base": {"__rl": true, "mode": "list", "value": "appXXX"}}
   ```

4. **Don't ignore error handling**
   - Use `alwaysOutputData: true` for search
   - Add If nodes to check for empty results
   - Use `ignoreErrors: true` in batch operations

5. **Don't mix node versions**
   - Keep all Airtable nodes at same version
   - Migrate old workflows to v2.1

6. **Don't forget to handle special characters in field names**
   ```json
   // Use bracket notation
   "={{ $json['Field with Spaces'] }}"
   "={{ $json['You have Subscription ?'] }}"
   ```

---

## 12. Troubleshooting Guide

### Common Issues

#### Issue: "Record not found" on update
**Solution:** Add `alwaysOutputData: true` and check if search returns results before update.

```json
{
  "name": "Search First",
  "operation": "search",
  "alwaysOutputData": true
}
```

Then use If node to route to Create or Update.

---

#### Issue: Linked records not working
**Solution:** Wrap record IDs in array brackets.

```json
// WRONG
"Project": "={{ $json.projectId }}"

// RIGHT
"Project": "={{ [$json.projectId] }}"
```

---

#### Issue: Date format errors
**Solution:** Use ISO format or Airtable-compatible date strings.

```json
"Date": "={{ new Date().toISOString() }}"
"Date": "={{ $now }}"
"Date": "={{ $json.date }}"  // If already in ISO format
```

---

#### Issue: Select field value not matching
**Solution:** Ensure option values exactly match Airtable field options.

```json
{
  "schema": [
    {
      "id": "Status",
      "type": "options",
      "options": [
        {"name": "Active", "value": "Active"}  // Must match exactly
      ]
    }
  ]
}
```

---

#### Issue: Credentials not working
**Solution:** Verify Personal Access Token has required scopes:
- `data.records:read`
- `data.records:write`
- `schema.bases:read`

---

#### Issue: Expression evaluation errors
**Solution:** Use proper expression syntax and null-safe operators.

```json
// Use optional chaining
"={{ $json.user?.email }}"

// Check for existence
"={{ $json.count ? $json.count : 0 }}"
```

---

## 13. Complete Workflow Examples

### Example 1: Form to Airtable to Slack

**Workflow Structure:**
```
Webhook Trigger → Transform Data → Airtable Create → Slack Notification
```

**Full Workflow JSON:**
```json
{
  "name": "Form to Airtable",
  "nodes": [
    {
      "id": "webhook-node",
      "name": "Form Webhook",
      "type": "n8n-nodes-base.webhook",
      "typeVersion": 1,
      "position": [250, 300],
      "webhookId": "unique-webhook-id"
    },
    {
      "id": "set-node",
      "name": "Transform",
      "type": "n8n-nodes-base.set",
      "typeVersion": 3,
      "position": [450, 300],
      "parameters": {
        "assignments": {
          "assignments": [
            {
              "id": "name-field",
              "name": "name",
              "value": "={{ $json.body.name }}",
              "type": "string"
            },
            {
              "id": "email-field",
              "name": "email",
              "value": "={{ $json.body.email }}",
              "type": "string"
            }
          ]
        },
        "options": {}
      }
    },
    {
      "id": "airtable-node",
      "name": "Save to Airtable",
      "type": "n8n-nodes-base.airtable",
      "typeVersion": 2.1,
      "position": [650, 300],
      "parameters": {
        "base": {
          "__rl": true,
          "mode": "list",
          "value": "appYourBaseId",
          "cachedResultName": "Form Submissions"
        },
        "table": {
          "__rl": true,
          "mode": "list",
          "value": "tblYourTableId",
          "cachedResultName": "Submissions"
        },
        "operation": "create",
        "columns": {
          "value": {
            "Name": "={{ $json.name }}",
            "Email": "={{ $json.email }}",
            "Submitted At": "={{ $now }}"
          },
          "mappingMode": "defineBelow"
        },
        "options": {
          "typecast": true
        }
      },
      "credentials": {
        "airtableTokenApi": {
          "id": "your-credential-id",
          "name": "Airtable PAT"
        }
      }
    },
    {
      "id": "slack-node",
      "name": "Notify Slack",
      "type": "n8n-nodes-base.slack",
      "typeVersion": 2,
      "position": [850, 300],
      "parameters": {
        "channel": "#submissions",
        "text": "New form submission from {{ $json.name }}"
      }
    }
  ],
  "connections": {
    "Form Webhook": {
      "main": [[{"node": "Transform", "type": "main", "index": 0}]]
    },
    "Transform": {
      "main": [[{"node": "Save to Airtable", "type": "main", "index": 0}]]
    },
    "Save to Airtable": {
      "main": [[{"node": "Notify Slack", "type": "main", "index": 0}]]
    }
  }
}
```

---

### Example 2: Scheduled ETL Pipeline

**Workflow Structure:**
```
Schedule → API Call → Transform → Dedupe → Airtable Upsert → Email Report
```

**Key Nodes:**
```json
{
  "nodes": [
    {
      "name": "Daily Schedule",
      "type": "n8n-nodes-base.scheduleTrigger",
      "parameters": {
        "rule": {
          "interval": [
            {"field": "cronExpression", "expression": "0 9 * * *"}
          ]
        }
      }
    },
    {
      "name": "Fetch Data",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "https://api.example.com/leads",
        "method": "GET"
      }
    },
    {
      "name": "Remove Duplicates",
      "type": "n8n-nodes-base.removeDuplicates",
      "parameters": {
        "compare": "selectedFields",
        "fieldsToCompare": "email"
      }
    },
    {
      "name": "Upsert to Airtable",
      "type": "n8n-nodes-base.airtable",
      "typeVersion": 2.1,
      "parameters": {
        "operation": "upsert",
        "columns": {
          "value": {
            "email": "={{ $json.email }}",
            "company": "={{ $json.company }}",
            "status": "New"
          },
          "matchingColumns": ["email"]
        },
        "options": {
          "typecast": true,
          "bulkSize": 10
        }
      }
    }
  ]
}
```

---

## 14. Advanced Patterns

### 14.1 Conditional Create or Update

```json
{
  "nodes": [
    {
      "name": "Search Existing",
      "type": "n8n-nodes-base.airtable",
      "parameters": {
        "operation": "search",
        "filterByFormula": "={Email} = '{{ $json.email }}'",
        "alwaysOutputData": true
      }
    },
    {
      "name": "If Exists",
      "type": "n8n-nodes-base.if",
      "parameters": {
        "conditions": {
          "number": [
            {
              "value1": "={{ $json.length }}",
              "operation": "larger",
              "value2": 0
            }
          ]
        }
      }
    },
    {
      "name": "Update Record",
      "type": "n8n-nodes-base.airtable",
      "parameters": {
        "operation": "update",
        "columns": {
          "matchingColumns": ["Email"]
        }
      }
    },
    {
      "name": "Create Record",
      "type": "n8n-nodes-base.airtable",
      "parameters": {
        "operation": "create"
      }
    }
  ],
  "connections": {
    "Search Existing": {
      "main": [[{"node": "If Exists", "type": "main", "index": 0}]]
    },
    "If Exists": {
      "main": [
        [{"node": "Update Record", "type": "main", "index": 0}],
        [{"node": "Create Record", "type": "main", "index": 0}]
      ]
    }
  }
}
```

---

### 14.2 Batch Processing with Rate Limiting

```json
{
  "nodes": [
    {
      "name": "Get All Records",
      "type": "n8n-nodes-base.airtable",
      "parameters": {
        "operation": "list",
        "returnAll": true
      }
    },
    {
      "name": "Split in Batches",
      "type": "n8n-nodes-base.splitInBatches",
      "parameters": {
        "batchSize": 5,
        "options": {}
      }
    },
    {
      "name": "Process Item",
      "type": "n8n-nodes-base.code",
      "parameters": {
        "mode": "runOnceForAllItems"
      }
    },
    {
      "name": "Wait 1 Second",
      "type": "n8n-nodes-base.wait",
      "parameters": {
        "unit": "seconds",
        "amount": 1
      }
    },
    {
      "name": "Update Airtable",
      "type": "n8n-nodes-base.airtable",
      "parameters": {
        "operation": "update"
      }
    }
  ]
}
```

---

### 14.3 AI-Powered Data Enrichment

```json
{
  "nodes": [
    {
      "name": "Get Pending Records",
      "type": "n8n-nodes-base.airtable",
      "parameters": {
        "operation": "search",
        "filterByFormula": "={Status} = 'Pending'"
      }
    },
    {
      "name": "AI Categorize",
      "type": "n8n-nodes-base.openAi",
      "parameters": {
        "operation": "message",
        "text": "Categorize this company: {{ $json.company_name }}"
      }
    },
    {
      "name": "Update with AI Results",
      "type": "n8n-nodes-base.airtable",
      "typeVersion": 2.1,
      "parameters": {
        "operation": "update",
        "columns": {
          "value": {
            "Category": "={{ $json.category }}",
            "Status": "Processed",
            "Processed At": "={{ $now }}"
          },
          "matchingColumns": ["id"]
        }
      }
    }
  ]
}
```

---

## 15. Quick Reference Tables

### Node Type Versions

| Version | Auth Method | Status | Use For |
|---------|-------------|--------|---------|
| 1 | API Key | Legacy | Existing workflows only |
| 2.1 | Personal Access Token | Current | All new workflows |

### Operations Quick Reference

| Operation | Purpose | Key Parameters | Returns |
|-----------|---------|----------------|---------|
| `create` | Add new record | `columns.value` | Created record |
| `update` | Modify existing | `matchingColumns` | Updated record |
| `upsert` | Create or update | `matchingColumns` | Created/updated record |
| `search` | Query records | `filterByFormula` | Matching records |
| `list` | Get all records | `limit`, `filterByFormula` | All/filtered records |
| `getSchema` | Get metadata | `base` | Base/table schema |

### Field Types Reference

| Type | JSON Type | Example Value |
|------|-----------|---------------|
| `string` | String | `"John Doe"` |
| `number` | Number | `42` |
| `boolean` | Boolean | `true` / `false` |
| `dateTime` | ISO String | `"2025-01-09T12:00:00Z"` |
| `options` | String | `"Active"` |
| `array` | Array | `["tag1", "tag2"]` |

### Expression Functions

| Function | Purpose | Example |
|----------|---------|---------|
| `$json.field` | Access current item | `={{ $json.name }}` |
| `$('Node').item.json.field` | Access other node | `={{ $('Webhook').item.json.email }}` |
| `$now` | Current timestamp | `={{ $now }}` |
| `$now.format()` | Formatted date | `={{ $now.format('yyyy-MM-dd') }}` |
| `.toNumber()` | Convert to number | `={{ $json.id.toNumber() }}` |
| `.toLowerCase()` | Lowercase string | `={{ $json.name.toLowerCase() }}` |

---

## 16. Version Migration Guide

### Migrating from TypeVersion 1 to 2.1

**Before (v1):**
```json
{
  "typeVersion": 1,
  "parameters": {
    "application": "appXXXXXXXXXXXXXX",
    "table": "Table 1",
    "operation": "append"
  },
  "credentials": {
    "airtableApi": "Airtable Credentials"
  }
}
```

**After (v2.1):**
```json
{
  "typeVersion": 2.1,
  "parameters": {
    "base": {
      "__rl": true,
      "mode": "list",
      "value": "appXXXXXXXXXXXXXX",
      "cachedResultName": "My Base"
    },
    "table": {
      "__rl": true,
      "mode": "list",
      "value": "tblYYYYYYYYYYYYYY",
      "cachedResultName": "Table 1"
    },
    "operation": "create",
    "columns": {
      "mappingMode": "autoMapInputData"
    }
  },
  "credentials": {
    "airtableTokenApi": {
      "id": "credential-id",
      "name": "Airtable PAT"
    }
  }
}
```

**Key Changes:**
1. `application` → `base` (resource locator object)
2. `table` → `table` (resource locator object)
3. `append` → `create`
4. `airtableApi` → `airtableTokenApi` (with id/name)
5. New `columns` parameter structure

---

## 17. Security Best Practices

1. **Use Personal Access Tokens with Minimum Scopes**
   - Only grant necessary permissions
   - Create separate tokens for different workflows

2. **Avoid Hardcoding Credentials**
   - Use n8n credential system
   - Never expose API keys in workflow JSON

3. **Implement Error Handling**
   - Use `ignoreErrors` for batch operations
   - Add If nodes to validate data before write

4. **Validate Input Data**
   - Check for required fields before Airtable operations
   - Sanitize user input to prevent formula injection

5. **Use Environment Variables for Base/Table IDs**
   - Store in n8n environment variables
   - Reference with `={{ $env.AIRTABLE_BASE_ID }}`

---

## 18. Performance Optimization

### Batch Operations

```json
{
  "options": {
    "bulkSize": 10  // Process 10 records at a time
  }
}
```

### Return Only Needed Fields

```json
{
  "operation": "list",
  "options": {
    "fields": ["Name", "Email", "Status"]  // Only return these fields
  }
}
```

### Use Filters to Reduce Data

```json
{
  "operation": "search",
  "filterByFormula": "={Status} = 'Active'",
  "limit": 100
}
```

### Limit Record Count

```json
{
  "returnAll": false,
  "limit": 50
}
```

---

## 19. Appendix: Full Node Templates

### Template A: Basic Create Node

```json
{
  "id": "unique-node-id",
  "name": "Create Airtable Record",
  "type": "n8n-nodes-base.airtable",
  "typeVersion": 2.1,
  "position": [900, 300],
  "parameters": {
    "base": {
      "__rl": true,
      "mode": "list",
      "value": "YOUR_BASE_ID",
      "cachedResultName": "Your Base Name"
    },
    "table": {
      "__rl": true,
      "mode": "list",
      "value": "YOUR_TABLE_ID",
      "cachedResultName": "Your Table Name"
    },
    "operation": "create",
    "columns": {
      "value": {
        "FieldName1": "={{ $json.field1 }}",
        "FieldName2": "={{ $json.field2 }}"
      },
      "mappingMode": "defineBelow"
    },
    "options": {
      "typecast": true
    }
  },
  "credentials": {
    "airtableTokenApi": {
      "id": "YOUR_CREDENTIAL_ID",
      "name": "Airtable Personal Access Token"
    }
  }
}
```

### Template B: Search and Update

```json
{
  "nodes": [
    {
      "id": "search-node",
      "name": "Search Record",
      "type": "n8n-nodes-base.airtable",
      "typeVersion": 2.1,
      "parameters": {
        "base": {"__rl": true, "mode": "list", "value": "BASE_ID"},
        "table": {"__rl": true, "mode": "list", "value": "TABLE_ID"},
        "operation": "search",
        "filterByFormula": "={Email} = '{{ $json.email }}'",
        "alwaysOutputData": true
      }
    },
    {
      "id": "update-node",
      "name": "Update Record",
      "type": "n8n-nodes-base.airtable",
      "typeVersion": 2.1,
      "parameters": {
        "base": {"__rl": true, "mode": "list", "value": "BASE_ID"},
        "table": {"__rl": true, "mode": "list", "value": "TABLE_ID"},
        "operation": "update",
        "columns": {
          "value": {
            "Status": "Updated",
            "Last Modified": "={{ $now }}"
          },
          "matchingColumns": ["Email"]
        }
      }
    }
  ]
}
```

### Template C: Upsert with Complex Schema

```json
{
  "name": "Upsert Lead",
  "type": "n8n-nodes-base.airtable",
  "typeVersion": 2.1,
  "parameters": {
    "base": {"__rl": true, "mode": "list", "value": "BASE_ID"},
    "table": {"__rl": true, "mode": "list", "value": "TABLE_ID"},
    "operation": "upsert",
    "columns": {
      "value": {
        "Email": "={{ $json.email }}",
        "Name": "={{ $json.name }}",
        "Company": "={{ $json.company }}",
        "Status": "New",
        "Score": "={{ $json.score }}",
        "Tags": "={{ $json.tags }}",
        "Created": "={{ $now }}"
      },
      "schema": [
        {"id": "Email", "type": "string", "canBeUsedToMatch": true},
        {"id": "Name", "type": "string"},
        {"id": "Company", "type": "string"},
        {
          "id": "Status",
          "type": "options",
          "options": [
            {"name": "New", "value": "New"},
            {"name": "Contacted", "value": "Contacted"},
            {"name": "Qualified", "value": "Qualified"}
          ]
        },
        {"id": "Score", "type": "number"},
        {"id": "Tags", "type": "array"},
        {"id": "Created", "type": "dateTime"}
      ],
      "mappingMode": "defineBelow",
      "matchingColumns": ["Email"]
    },
    "options": {
      "typecast": true
    }
  },
  "credentials": {
    "airtableTokenApi": {
      "id": "CREDENTIAL_ID",
      "name": "Airtable PAT"
    }
  }
}
```

---

## 20. Glossary

| Term | Definition |
|------|------------|
| **Base** | Top-level container in Airtable (like a database) |
| **Table** | Collection of records within a base (like a table) |
| **Record** | Single row of data in a table |
| **Field** | Column in a table with specific data type |
| **Formula** | Airtable's query language for filtering |
| **Resource Locator** | n8n's method for selecting bases/tables |
| **Typecast** | Automatic data type conversion |
| **PAT** | Personal Access Token (modern auth method) |
| **Upsert** | Update if exists, insert if not |
| **Schema** | Definition of field types and properties |
| **Matching Columns** | Fields used to identify records for update |
| **Mapping Mode** | How input data is mapped to Airtable fields |

---

## Document Metadata

**Analysis Sources:**
- 100+ production n8n workflows
- TypeVersion 1 and 2.1 implementations
- Real-world use cases across industries

**Node Versions Covered:**
- Airtable Node: v1, v2.1
- Airtable Trigger: v1

**Categories Analyzed:**
- AI workflows
- Sales/CRM workflows
- Marketing automation
- Social media management
- Support/ticketing systems
- Product management
- Personal productivity

**Last Analysis Date:** 2025-11-09

---

## Usage Instructions for AI Agents

When building n8n workflows with Airtable:

1. **Always use TypeVersion 2.1** with PAT authentication
2. **Copy exact JSON structure** from templates
3. **Replace placeholder IDs** with actual base/table/credential IDs
4. **Validate field types** match Airtable schema
5. **Use appropriate operation** for your use case (create/update/upsert/search)
6. **Enable typecast** unless you need strict type validation
7. **Handle errors** with alwaysOutputData and If nodes
8. **Test with small datasets** before production deployment

For questions or updates to this knowledge base, refer to source workflows in `/home/user/n8n-master-workflows/`.

---

**END OF KNOWLEDGE BASE**
