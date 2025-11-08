# Airtable Workflows - Quick Reference Guide

## 📊 Statistics at a Glance

- **Total Workflows**: ~100
- **Node Types**: 3 (airtable, airtableTrigger, airtableTool)
- **Categories**: 14+ business domains
- **Integration Partners**: 40+ services

## 🔝 Top Operations

1. **CREATE** (40%) - Store new records
2. **SEARCH** (25%) - Find existing records
3. **UPDATE** (20%) - Modify records
4. **LIST** (10%) - Retrieve all records
5. **DELETE** (5%) - Remove records

## 🔗 Most Common Integrations

1. **Airtable + OpenAI** (15+ workflows) - AI-enhanced data
2. **Airtable + WhatsApp** (12+ workflows) - Conversational interfaces
3. **Airtable + Typeform** (8+ workflows) - Form submissions
4. **Airtable + LinkedIn** (10+ workflows) - Lead generation
5. **Airtable + Slack** (8+ workflows) - Notifications

## 📁 By Category

| Category | Count | Top Use Cases |
|----------|-------|---------------|
| Sales | 18 | CRM, Lead Gen, Order Tracking |
| Social Media | 12 | Engagement, Content, Analytics |
| Support | 10 | Tickets, Chatbots, Transcripts |
| Product | 10 | Forms, Analytics, Tasks |
| Marketing | 8 | Campaigns, Content, Leads |
| HR | 7 | Recruiting, Employee DB |
| AI/Chatbot | 7 | Natural Language, Agents |
| Multimodal AI | 8 | Image/Video + Data |

## 🎯 Common Use Cases

### Data Collection (50%)
- Form submissions
- Webhook captures
- API data storage

### CRM & Leads (20%)
- Contact management
- Lead qualification
- Company research

### Social Media (12%)
- Engagement tracking
- Content scheduling
- Analytics storage

### Automation (18%)
- Task creation
- Reporting
- Notifications

## 💡 Quick Examples

### Simple Create
```
Form → Airtable CREATE
```

### Search & Update
```
Webhook → Airtable SEARCH → Update Count → Airtable UPDATE
```

### Daily Report
```
Schedule → Airtable SEARCH → Format → Email
```

### AI Agent
```
Chat → AI Agent (with Airtable Tools) → Response
```

## 📝 Common Table Fields

**CRM Tables**:
- Name, Email, Phone
- Company, Website, LinkedIn
- Status, Category
- Notes, Created Date

**Order Tables**:
- orderID, customerID
- orderPrice, orderStatus
- time, date

**Engagement Tables**:
- User_ID
- Count (points/messages)
- Last interaction
- Raffle vouchers

## 🔐 Authentication

**Modern (Recommended)**:
```json
{
  "credentials": {
    "airtableTokenApi": {
      "id": "xxx",
      "name": "Personal Access Token"
    }
  }
}
```

## 📌 Key Configuration Patterns

### Create with Fields
```json
{
  "operation": "create",
  "columns": {
    "mappingMode": "defineBelow",
    "value": {
      "Name": "={{ $json.Name }}",
      "Email": "={{ $json.email }}"
    }
  }
}
```

### Search with Formula
```json
{
  "operation": "search",
  "filterByFormula": "={FieldName} = 'value'"
}
```

### Update with Matching
```json
{
  "operation": "update",
  "columns": {
    "matchingColumns": ["id"],
    "value": { /* updates */ }
  }
}
```

## 🚀 Best Practices

1. ✅ Use Personal Access Tokens
2. ✅ Check for duplicates before CREATE
3. ✅ Use typecast option for numbers
4. ✅ Store timestamps for tracking
5. ✅ Use filterByFormula for searches
6. ✅ Enable alwaysOutputData for searches

## 📖 Full Documentation

See `AIRTABLE_WORKFLOWS_COMPREHENSIVE_ANALYSIS.md` for:
- Detailed workflow examples
- Complete configuration patterns
- Integration deep-dives
- Full workflow inventory
- Advanced patterns

## 🔍 Find Workflows By Need

**Form Data Storage**: `Store_Form_Submission_in_Airtable.json`
**CRM Building**: `Search_LinkedIn_companies_and_add_them_to_Airtable_CRM.json`
**Engagement Tracking**: `Track_WhatsApp_Group_Message_Activity_with_Airtable_Database.json`
**AI Integration**: `AI-Powered_Contact_Management_in_Airtable_with_Natural_Language_Commands.json`
**Scheduled Reports**: `Send_Weekly_Engagement_Stats_Raffle_Updates_via_WhatsApp_using_Airtable.json`
**Order Management**: `Store_new_orders_to_Airtable_and_summarize_daily_orders_through_email.json`

---

**Quick Access**: All workflow files are in their respective category directories:
- `/Sales/`
- `/Social_Media/`
- `/Support/`
- `/Product/`
- `/Marketing/`
- `/HR/`
- `/Other/`
