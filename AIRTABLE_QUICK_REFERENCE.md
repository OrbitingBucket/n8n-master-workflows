# n8n Airtable Node Quick Reference

**Last Updated:** 2025-11-09
**Purpose:** Quick copy-paste reference for common Airtable operations

---

## Basic Node Structure (TypeVersion 2.1)

```json
{
  "name": "Airtable Node",
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
      "value": "tblYYYYYYYYYYYYYY"
    },
    "operation": "create"
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

## CREATE - Store New Data

### Simple Create (Auto-Map)
```json
{
  "operation": "create",
  "columns": {
    "mappingMode": "autoMapInputData"
  },
  "options": {
    "typecast": true
  }
}
```

### Create with Field Mapping
```json
{
  "operation": "create",
  "columns": {
    "value": {
      "Name": "={{ $json.name }}",
      "Email": "={{ $json.email }}",
      "Status": "New",
      "Created": "={{ $now }}"
    },
    "mappingMode": "defineBelow"
  },
  "options": {
    "typecast": true
  }
}
```

### Create with Complex Schema
```json
{
  "operation": "create",
  "columns": {
    "value": {
      "Name": "={{ $json.name }}",
      "Priority": "High",
      "Due Date": "={{ $json.dueDate }}",
      "Project": "={{ [$json.projectId] }}",
      "Tags": "={{ $json.tags }}"
    },
    "schema": [
      {
        "id": "Priority",
        "type": "options",
        "options": [
          {"name": "Low", "value": "Low"},
          {"name": "Medium", "value": "Medium"},
          {"name": "High", "value": "High"}
        ]
      },
      {"id": "Due Date", "type": "dateTime"},
      {"id": "Project", "type": "array"},
      {"id": "Tags", "type": "array"}
    ],
    "mappingMode": "defineBelow"
  },
  "options": {
    "typecast": true
  }
}
```

---

## UPDATE - Modify Existing Records

### Update by Email
```json
{
  "operation": "update",
  "columns": {
    "value": {
      "Email": "={{ $json.email }}",
      "Status": "Updated",
      "Last Modified": "={{ $now }}"
    },
    "matchingColumns": ["Email"]
  }
}
```

### Update by Multiple Fields
```json
{
  "operation": "update",
  "columns": {
    "value": {
      "User_ID": "={{ $json.userId }}",
      "Count": "={{ $json.count }}",
      "Last Interaction": "={{ $now.format('yyyy.MM.dd') }}"
    },
    "matchingColumns": ["User_ID"]
  }
}
```

⚠️ **Critical:** Always specify `matchingColumns` for updates!

---

## UPSERT - Update or Create

### Basic Upsert
```json
{
  "operation": "upsert",
  "columns": {
    "value": {
      "email": "={{ $json.email }}",
      "name": "={{ $json.name }}",
      "company": "={{ $json.company }}",
      "status": "Active"
    },
    "matchingColumns": ["email"]
  },
  "options": {
    "typecast": true
  }
}
```

### Upsert for CRM
```json
{
  "operation": "upsert",
  "columns": {
    "value": {
      "email": "={{ $json.email }}",
      "first_name": "={{ $json.firstName }}",
      "last_name": "={{ $json.lastName }}",
      "company": "={{ $json.company }}",
      "linkedin_url": "={{ $json.linkedinUrl }}",
      "status": "New Lead",
      "score": "={{ $json.score }}",
      "last_updated": "={{ $now }}"
    },
    "matchingColumns": ["email"]
  }
}
```

---

## SEARCH - Query Records

### Search by Single Field
```json
{
  "operation": "search",
  "filterByFormula": "={Email} = '{{ $json.email }}'",
  "alwaysOutputData": true
}
```

### Search with AND Condition
```json
{
  "operation": "search",
  "filterByFormula": "=AND({Status} = 'Active', {Score} > 15)"
}
```

### Search Date Range
```json
{
  "operation": "search",
  "filterByFormula": "=AND({Date} >= '2025-01-01', {Date} <= '2025-12-31')"
}
```

### Search with Dynamic Dates
```json
{
  "operation": "search",
  "filterByFormula": "=AND(time < \"{{ $json.now }}\", time > \"{{ $json.yesterday }}\")"
}
```

### Search with OR Condition
```json
{
  "operation": "search",
  "filterByFormula": "=OR({Type} = 'A', {Type} = 'B', {Type} = 'C')"
}
```

### Search Not Empty
```json
{
  "operation": "search",
  "filterByFormula": "=AND(url != \"\", {title} = \"\")"
}
```

💡 **Tip:** Always use `alwaysOutputData: true` for searches!

---

## LIST - Get All Records

### List All Records
```json
{
  "operation": "list",
  "returnAll": true
}
```

### List with Limit
```json
{
  "operation": "list",
  "returnAll": false,
  "limit": 100
}
```

### List Specific Fields
```json
{
  "operation": "list",
  "options": {
    "fields": ["Name", "Email", "Status"]
  },
  "returnAll": true
}
```

### List with Filter
```json
{
  "operation": "list",
  "options": {
    "filterByFormula": "{Status} = 'Active'"
  },
  "returnAll": true
}
```

---

## Field Type Examples

### String
```json
{
  "Name": "={{ $json.name }}",
  "Description": "Static text value"
}
```

### Number
```json
{
  "Price": "={{ $json.price }}",
  "Quantity": 42,
  "Total": "={{ $json.price * $json.quantity }}"
}
```

### Boolean
```json
{
  "IsActive": "={{ $json.active }}",
  "HasSubscription": true
}
```

### DateTime
```json
{
  "Created": "={{ $now }}",
  "Updated": "={{ new Date().toISOString() }}",
  "Formatted": "={{ $now.format('yyyy.MM.dd') }}",
  "FromInput": "={{ $json.date }}"
}
```

### Single Select (Options)
```json
{
  "columns": {
    "value": {
      "Status": "Active"
    },
    "schema": [
      {
        "id": "Status",
        "type": "options",
        "options": [
          {"name": "Active", "value": "Active"},
          {"name": "Inactive", "value": "Inactive"}
        ]
      }
    ]
  }
}
```

### Multiple Select (Array)
```json
{
  "Tags": "={{ $json.tags }}"
}
```

### Linked Record (Single)
```json
{
  "Project": "={{ [$json.projectId] }}"
}
```
⚠️ **Note:** Single linked records must be wrapped in array brackets!

### Linked Record (Multiple)
```json
{
  "Projects": "={{ $json.projectIds }}"
}
```

---

## Expression Reference

### Current Item
```javascript
={{ $json.fieldName }}
={{ $json.body.messages[0].from }}
={{ $json['Field with Spaces'] }}
```

### Previous Node
```javascript
={{ $('NodeName').item.json.fieldName }}
={{ $node['NodeName'].json.fieldName }}
```

### Date/Time
```javascript
={{ $now }}
={{ $now.format('yyyy.MM.dd') }}
={{ $now.format('yyyy-MM-dd HH:mm:ss') }}
={{ new Date().toISOString() }}
```

### String Operations
```javascript
={{ $json.name.toLowerCase() }}
={{ $json.name.toUpperCase() }}
={{ $json.value.trim() }}
```

### Type Conversion
```javascript
={{ $json.id.toNumber() }}
={{ String($json.value) }}
={{ JSON.stringify($json.object) }}
```

### Conditional
```javascript
={{ $json.status === 'active' ? 'Active' : 'Inactive' }}
={{ $json.count > 10 ? 'High' : 'Low' }}
```

### Optional Chaining
```javascript
={{ $json.user?.email }}
={{ $json.data?.optional?.field }}
```

---

## Common Workflow Patterns

### 1. Form to Airtable
```
Webhook → Set (transform) → Airtable (create) → Slack
```

### 2. Check Before Create
```
Data → Airtable (search) → If → Create or Update
```

**If Condition:**
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

### 3. Scheduled Report
```
Schedule → Airtable (search with date) → HTML → Email
```

### 4. ETL Pipeline
```
Schedule → HTTP (API) → Code → Remove Duplicates → Airtable (upsert)
```

### 5. Batch Processing
```
Airtable (list) → Split in Batches → Process → Update → Loop
```

---

## Airtable Trigger Node

```json
{
  "name": "Airtable Trigger",
  "type": "n8n-nodes-base.airtableTrigger",
  "typeVersion": 1,
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
  },
  "credentials": {
    "airtableApi": {
      "id": "8",
      "name": "Airtable account"
    }
  }
}
```

---

## Resource Locator Modes

### Mode: list (Dropdown Selection)
```json
{
  "base": {
    "__rl": true,
    "mode": "list",
    "value": "appXXXXXXXXXXXXXX",
    "cachedResultName": "My Base"
  }
}
```

### Mode: id (Dynamic/Expression)
```json
{
  "base": {
    "__rl": true,
    "mode": "id",
    "value": "={{ $json.baseId }}"
  }
}
```

### Mode: url (URL-based)
```json
{
  "base": {
    "__rl": true,
    "mode": "url",
    "value": "https://airtable.com/appXXXXXXXXXXXXXX"
  }
}
```

---

## Common Options

```json
{
  "options": {
    "typecast": true,           // Auto-convert types (recommended)
    "bulkSize": 10,             // Batch size for processing
    "ignoreErrors": true,       // Continue on errors
    "fields": ["Name", "Email"] // Specific fields to return
  }
}
```

---

## Node Properties

```json
{
  "alwaysOutputData": true,  // Output data even if empty
  "executeOnce": false,      // Execute once for all items
  "position": [900, 300]     // Canvas position
}
```

---

## Troubleshooting Quick Fixes

### Issue: Update fails "record not found"
**Fix:** Use search first with `alwaysOutputData: true`

### Issue: Linked records not saving
**Fix:** Wrap in array: `"={{ [$json.recordId] }}"`

### Issue: Date errors
**Fix:** Use ISO format: `"={{ $now }}"` or `"={{ new Date().toISOString() }}"`

### Issue: Select field mismatch
**Fix:** Ensure exact match with Airtable options

### Issue: Field with spaces
**Fix:** Use bracket notation: `"={{ $json['Field Name'] }}"`

---

## Complete Examples

### Example 1: Store Form Submission
```json
{
  "name": "Save Form",
  "type": "n8n-nodes-base.airtable",
  "typeVersion": 2.1,
  "parameters": {
    "base": {
      "__rl": true,
      "mode": "list",
      "value": "appFormBase"
    },
    "table": {
      "__rl": true,
      "mode": "list",
      "value": "tblSubmissions"
    },
    "operation": "create",
    "columns": {
      "value": {
        "Name": "={{ $json.name }}",
        "Email": "={{ $json.email }}",
        "Message": "={{ $json.message }}",
        "Submitted": "={{ $now }}"
      },
      "mappingMode": "defineBelow"
    },
    "options": {
      "typecast": true
    }
  },
  "credentials": {
    "airtableTokenApi": {
      "id": "cred-id",
      "name": "Airtable PAT"
    }
  }
}
```

### Example 2: Track User Engagement
```json
{
  "name": "Update User",
  "type": "n8n-nodes-base.airtable",
  "typeVersion": 2.1,
  "parameters": {
    "operation": "update",
    "columns": {
      "value": {
        "User_ID": "={{ $json.userId }}",
        "Count": "={{ $json.count + 1 }}",
        "Last Visit": "={{ $now.format('yyyy.MM.dd') }}"
      },
      "matchingColumns": ["User_ID"]
    }
  }
}
```

### Example 3: CRM Lead Upsert
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
        "status": "New Lead"
      },
      "matchingColumns": ["email"]
    },
    "options": {
      "typecast": true
    }
  }
}
```

### Example 4: Search Active Records
```json
{
  "name": "Find Active",
  "type": "n8n-nodes-base.airtable",
  "typeVersion": 2.1,
  "parameters": {
    "operation": "search",
    "filterByFormula": "=AND({Status} = 'Active', {Score} > 10)",
    "options": {
      "fields": ["Name", "Email", "Score"]
    }
  },
  "alwaysOutputData": true
}
```

---

## Formula Cheat Sheet

| Pattern | Formula |
|---------|---------|
| Exact match | `={Field} = 'value'` |
| Numeric comparison | `={Score} > 15` |
| AND condition | `=AND({A} = 'x', {B} > 5)` |
| OR condition | `=OR({Type} = 'A', {Type} = 'B')` |
| Date range | `=AND({Date} >= '2025-01-01', {Date} <= '2025-12-31')` |
| Not empty | `={Field} != ''` |
| With expression | `={Email} = '{{ $json.email }}'` |
| Multiple AND | `=AND({A} = 'x', {B} = 'y', {C} > 10)` |
| Starts with | `=FIND('prefix', {Field}) = 1` |
| Contains | `=FIND('text', {Field}) > 0` |

---

## Best Practices Checklist

✅ Use TypeVersion 2.1
✅ Enable `typecast: true`
✅ Use `alwaysOutputData: true` for searches
✅ Specify `matchingColumns` for update/upsert
✅ Wrap single linked records in arrays
✅ Use ISO date format
✅ Handle errors with If nodes
✅ Use Resource Locator objects

❌ Don't use TypeVersion 1
❌ Don't forget matchingColumns
❌ Don't ignore error handling
❌ Don't mix node versions

---

**Quick Links:**
- Full Knowledge Base: `AIRTABLE_NODE_KNOWLEDGE_BASE.md`
- JSON Patterns: `AIRTABLE_NODE_PATTERNS.json`
- Airtable API Docs: https://airtable.com/developers/web/api/introduction
- n8n Airtable Node Docs: https://docs.n8n.io/integrations/builtin/app-nodes/n8n-nodes-base.airtable/
