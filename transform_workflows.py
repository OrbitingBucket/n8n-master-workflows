#!/usr/bin/env python3
"""
Transform technical workflow cards into business-friendly descriptions.
"""

import json
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import List, Dict, Any


def load_jsonl(filepath: str) -> List[Dict[str, Any]]:
    """Load JSONL file into list of dictionaries."""
    data = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                data.append(json.loads(line))
    return data


def load_json(filepath: str) -> Dict[str, Any]:
    """Load JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def generate_business_title(card: Dict[str, Any]) -> str:
    """Generate business-friendly title starting with verb + object."""

    # Start with original title
    original = card.get('title', '')

    # Extract key information
    category = card.get('category', '')
    use_tags = card.get('useCaseTags', [])
    airtable_ops = card.get('airtableUsage', {}).get('operations', {})
    integrations = card.get('nodes', {}).get('integrations', [])
    triggers = card.get('triggers', [])

    # If original title is descriptive and under 100 chars, use it with minor cleanup
    if original and len(original) < 100 and any(keyword in original.lower() for keyword in
        ['airtable', 'lead', 'email', 'form', 'automate', 'track', 'sync', 'generate', 'extract', 'monitor']):
        # Clean up original title
        cleaned = original.replace('_', ' ')
        # Remove redundant "with Airtable" if at the end and replace with "to Airtable"
        if cleaned.endswith(' and Airtable'):
            cleaned = cleaned[:-13] + ' to Airtable'
        return cleaned

    # Otherwise generate a business title
    # Verb mapping based on operations
    if 'upsert' in airtable_ops:
        verb = "Sync"
    elif 'create' in airtable_ops or 'append' in airtable_ops:
        verb = "Store"
    elif 'update' in airtable_ops:
        verb = "Update"
    elif 'search' in airtable_ops:
        verb = "Track"
    else:
        verb = "Manage"

    # Determine what's being processed based on category and use case
    object_part = "data"
    if 'lead-management' in use_tags or 'lead_generation' in use_tags or category == 'Lead_Generation':
        object_part = "leads"
    elif 'email' in use_tags or category == 'Email':
        object_part = "emails"
    elif 'messaging' in use_tags:
        object_part = "customer messages"
    elif category == 'Sales':
        object_part = "sales data"
    elif category == 'Marketing':
        object_part = "marketing campaigns"
    elif category == 'Support':
        object_part = "support tickets"
    elif category == 'HR':
        object_part = "employee records"
    elif category == 'Finance':
        object_part = "financial records"
    elif 'ai-powered' in use_tags:
        object_part = "AI-enriched data"
    elif 'automation' in use_tags:
        object_part = "workflow tasks"
    else:
        # Derive from integrations
        integration_mapping = {
            'typeform': 'form submissions',
            'gmail': 'emails',
            'telegram': 'Telegram messages',
            'whatsapp': 'WhatsApp conversations',
            'slack': 'Slack messages',
            'linkedin': 'LinkedIn data',
            'hubspot': 'HubSpot contacts',
            'salesforce': 'Salesforce records',
            'shopify': 'Shopify orders'
        }

        for key, value in integration_mapping.items():
            if any(key in i.lower() for i in integrations):
                object_part = value
                break

    # Check for specific source
    source = ""
    trigger_sources = {
        'formTrigger': 'from form submissions',
        'typeformTrigger': 'from Typeform',
        'gmailTrigger': 'from Gmail',
        'webhookTrigger': 'from webhooks',
        'telegramTrigger': 'from Telegram',
        'whatsAppTrigger': 'from WhatsApp',
        'shopifyTrigger': 'from Shopify',
        'airtableTrigger': 'between Airtable tables'
    }

    if triggers:
        trigger_type = triggers[0].get('type', '').lower()
        for key, value in trigger_sources.items():
            if key.lower() in trigger_type:
                source = value
                break

    # Construct title
    if source:
        title = f"{verb} {object_part} {source} in Airtable"
    else:
        title = f"{verb} {object_part} in Airtable"

    # Final cleanup
    title = title.replace('  ', ' ').strip()

    # If title is too generic, fall back to cleaned original
    if 'workflow data' in title.lower() or 'data data' in title.lower():
        if original:
            return original.replace('_', ' ')

    return title


def generate_one_liner(card: Dict[str, Any]) -> str:
    """Generate 18-24 word business-friendly one-liner."""

    category = card.get('category', '')
    use_tags = card.get('useCaseTags', [])
    airtable_ops = card.get('airtableUsage', {}).get('operations', {})
    triggers = card.get('triggers', [])

    # Determine trigger type
    trigger_type = "manual execution"
    if triggers:
        t = triggers[0].get('type', '')
        if 'schedule' in t.lower():
            trigger_type = "schedule"
        elif 'webhook' in t.lower():
            trigger_type = "webhook"
        elif 'form' in t.lower():
            trigger_type = "form submission"
        elif 'airtable' in t.lower():
            trigger_type = "Airtable updates"

    # Determine action
    action = "processes and stores"
    if 'upsert' in airtable_ops:
        action = "synchronizes"
    elif 'update' in airtable_ops:
        action = "updates"
    elif 'search' in airtable_ops:
        action = "finds and processes"

    # Determine value
    value = "organizing your data"
    if 'lead-management' in use_tags:
        value = "managing leads effectively"
    elif 'ai-powered' in use_tags:
        value = "using AI to enhance insights"
    elif 'automation' in use_tags:
        value = "saving time through automation"

    one_liner = f"Automatically {action} data in Airtable on {trigger_type}, {value} without manual effort."

    return one_liner


def generate_when_to_use(card: Dict[str, Any]) -> List[str]:
    """Generate 2-3 clear use case scenarios."""

    scenarios = []
    category = card.get('category', '')
    use_tags = card.get('useCaseTags', [])
    airtable_ops = card.get('airtableUsage', {}).get('operations', {})

    # Scenario mapping
    scenario_map = {
        'lead-management': "Track and manage sales leads from multiple sources",
        'lead_generation': "Generate and qualify new business leads",
        'email': "Organize and respond to customer emails",
        'messaging': "Handle customer communications across messaging platforms",
        'ai-powered': "Enhance data with AI-generated insights and analysis",
        'automation': "Automate repetitive data entry and processing tasks",
        'data-sync': "Keep data synchronized between systems",
    }

    # Add scenarios from tags
    for tag in use_tags:
        if tag in scenario_map and len(scenarios) < 3:
            scenarios.append(scenario_map[tag])

    # Add category-based scenarios
    category_scenarios = {
        'Sales': "Monitor sales pipeline and customer interactions",
        'Marketing': "Track campaign performance and leads",
        'Support': "Manage customer support tickets and responses",
        'HR': "Organize employee records and recruitment",
        'Finance': "Track expenses and financial records",
    }

    if category in category_scenarios and len(scenarios) < 3:
        scenarios.append(category_scenarios[category])

    # Add operation-based scenarios
    if 'upsert' in airtable_ops and len(scenarios) < 3:
        scenarios.append("Prevent duplicate records while keeping data up to date")

    # Ensure we have at least 2 scenarios
    if len(scenarios) < 2:
        scenarios.append("Centralize data from multiple sources in one place")
    if len(scenarios) < 2:
        scenarios.append("Automate data workflows to save time and reduce errors")

    return scenarios[:3]


def get_primary_trigger(card: Dict[str, Any]) -> Dict[str, str]:
    """Get primary trigger with webhook > schedule > manual priority."""

    triggers = card.get('triggers', [])
    if not triggers:
        return {"type": "manual", "details": "Manual execution"}

    # Priority order
    priority_order = ['webhook', 'form', 'schedule', 'airtable', 'gmail', 'telegram', 'whatsapp']

    for priority_type in priority_order:
        for trigger in triggers:
            t_type = trigger.get('type', '').lower()
            if priority_type in t_type:
                return {
                    "type": trigger.get('type', 'unknown'),
                    "details": trigger.get('details', '')
                }

    # Return first trigger if no priority match
    return {
        "type": triggers[0].get('type', 'unknown'),
        "details": triggers[0].get('details', '')
    }


def compress_dataflow(card: Dict[str, Any]) -> str:
    """Compress dataFlow.sketch into one ASCII line."""

    sketch = card.get('dataFlow', {}).get('sketch', '')
    if not sketch:
        return "trigger -> process -> store"

    # Extract node names
    parts = sketch.split(' -> ')
    if len(parts) <= 4:
        return sketch

    # Compress to first, middle marker, and last
    compressed = f"{parts[0]} -> ... ({len(parts)-2} steps) ... -> {parts[-1]}"

    # Limit length
    if len(compressed) > 100:
        compressed = f"{parts[0][:30]}... -> {parts[-1][:30]}..."

    return compressed


def determine_table_mode(card: Dict[str, Any]) -> str:
    """Determine if tables are dynamic, hardcoded, or mixed."""

    airtable_usage = card.get('airtableUsage', {})
    tables = airtable_usage.get('tables', [])
    bases = airtable_usage.get('bases', [])

    # If no tables/bases specified, likely dynamic (using resource locators)
    if not tables and not bases:
        return "dynamic"

    # If we have literal IDs
    if tables or bases:
        # Check if they look like placeholders
        placeholders = ['YOUR_TABLE_ID', 'YOUR_BASE_ID', 'Table 1', 'receipts']
        has_placeholder = any(p in str(tables) + str(bases) for p in placeholders)

        if has_placeholder:
            return "hardcoded"
        else:
            return "hardcoded"

    return "dynamic"


def generate_airtable_info(card: Dict[str, Any]) -> Dict[str, Any]:
    """Generate simplified Airtable configuration view."""

    airtable_usage = card.get('airtableUsage', {})

    # Determine table mode
    table_mode = determine_table_mode(card)

    # Get operations with count > 0
    operations_dict = airtable_usage.get('operations', {})
    operations = [op for op, count in operations_dict.items() if count > 0]

    # Get best filterByFormula examples
    filter_examples = airtable_usage.get('filterByFormulaExamples', [])[:3]

    # Determine if upsert pattern is used
    upsert = airtable_usage.get('usesUpsertPattern', False)
    matching_cols = airtable_usage.get('matchingColumnsExamples', [])
    if matching_cols or 'upsert' in operations:
        upsert = True

    # Pagination and rate limiting
    pagination = airtable_usage.get('usesPaginationLoop', False)
    rate_limiting = airtable_usage.get('usesWaitOrBackoff', False)

    return {
        "tables": table_mode,
        "operations": operations,
        "filterByFormulaExamples": filter_examples,
        "upsert": upsert,
        "pagination": pagination,
        "rateLimiting": rate_limiting
    }


def generate_setup_checklist(card: Dict[str, Any]) -> List[str]:
    """Generate specific and actionable setup checklist."""

    checklist = []

    # Always include Airtable PAT
    checklist.append("Configure Airtable Personal Access Token with data.records:read and data.records:write scopes")

    # Base/Table guidance
    table_mode = determine_table_mode(card)
    if table_mode == "dynamic":
        checklist.append("Use resource locators to select Base and Table dynamically from Airtable")
    else:
        checklist.append("Update hardcoded Base ID and Table ID with your Airtable workspace values")

    # Check for specific integrations
    integrations = card.get('nodes', {}).get('integrations', [])

    if any('whatsapp' in i.lower() for i in integrations):
        checklist.append("Set up WhatsApp Business API webhook and verify connection")

    if any('gmail' in i.lower() for i in integrations):
        checklist.append("Authorize Gmail API access with required email scopes")

    if any('openai' in i.lower() for i in integrations):
        checklist.append("Add OpenAI API key for AI-powered features")

    if any('slack' in i.lower() for i in integrations):
        checklist.append("Connect Slack workspace and configure webhook URL")

    if any('telegram' in i.lower() for i in integrations):
        checklist.append("Create Telegram Bot and add bot token to credentials")

    # Check for typecast needs
    airtable_ops = card.get('airtableUsage', {}).get('operations', {})
    if 'create' in airtable_ops or 'update' in airtable_ops or 'upsert' in airtable_ops:
        checklist.append("Enable typecast option if writing to number, date, or select fields")

    # Webhook setup
    triggers = card.get('triggers', [])
    if any('webhook' in t.get('type', '').lower() for t in triggers):
        checklist.append("Copy production webhook URL and configure in source system")

    return checklist


def transform_quality_notes(card: Dict[str, Any]) -> Dict[str, Any]:
    """Transform quality lints and scores."""

    quality = card.get('quality', {})
    lints = quality.get('lints', [])
    scores = quality.get('scores', {})

    # Convert lint strings to structured format
    structured_lints = []
    for lint in lints:
        if isinstance(lint, str):
            # Determine severity
            severity = "warning"
            if "error" in lint.lower() or "no error" in lint.lower():
                severity = "error"
            elif "rate limit" in lint.lower():
                severity = "error"

            structured_lints.append({
                "id": lint.lower().replace(' ', '_')[:50],
                "severity": severity,
                "message": lint
            })

    # Rename score keys
    renamed_scores = {
        "reliability": scores.get('reliabilityScore', 0),
        "maintainability": scores.get('maintainabilityScore', 0),
        "security": scores.get('securityScore', 0)
    }

    return {
        "lints": structured_lints,
        "scores": renamed_scores
    }


def extract_best_snippets(card: Dict[str, Any]) -> Dict[str, Any]:
    """Extract best filterByFormula and mapping examples."""

    snippets = {}

    airtable_usage = card.get('airtableUsage', {})

    # Filter formulas
    filter_examples = airtable_usage.get('filterByFormulaExamples', [])
    if filter_examples:
        snippets['filterByFormula'] = filter_examples[:2]

    # Matching columns (for upsert)
    matching_cols = airtable_usage.get('matchingColumnsExamples', [])
    if matching_cols:
        snippets['matchingColumns'] = matching_cols[:2]

    # Notable config
    notable = card.get('notableConfig', {})
    if notable:
        snippets['notableConfig'] = notable

    return snippets


def transform_workflow_card(card: Dict[str, Any]) -> Dict[str, Any]:
    """Transform a workflow card into a WorkflowDescription."""

    return {
        "filePath": card.get('filePath', ''),
        "title": generate_business_title(card),
        "oneLiner": generate_one_liner(card),
        "whenToUse": generate_when_to_use(card),
        "trigger": get_primary_trigger(card),
        "dataFlow": compress_dataflow(card),
        "airtable": generate_airtable_info(card),
        "integrations": card.get('nodes', {}).get('integrations', []),
        "setupChecklist": generate_setup_checklist(card),
        "qualityNotes": transform_quality_notes(card),
        "snippets": extract_best_snippets(card),
        "category": card.get('category', ''),
        "useCaseTags": card.get('useCaseTags', [])
    }


def generate_catalog(cards: List[Dict[str, Any]], descriptions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate catalog summary."""

    # Group by category
    by_category = defaultdict(list)
    for i, card in enumerate(cards):
        category = card.get('category', 'Other')
        reliability = card.get('quality', {}).get('scores', {}).get('reliabilityScore', 0)
        by_category[category].append({
            'file': card.get('filePath', ''),
            'reliability': reliability,
            'index': i
        })

    # Sort and get top 3 per category
    category_list = []
    for category, items in by_category.items():
        items.sort(key=lambda x: x['reliability'], reverse=True)
        top_3 = [item['file'] for item in items[:3]]
        category_list.append({
            'name': category,
            'count': len(items),
            'top': top_3
        })

    category_list.sort(key=lambda x: x['count'], reverse=True)

    # Group by pattern (based on operations and structure)
    pattern_examples = defaultdict(list)
    for card in cards:
        airtable_usage = card.get('airtableUsage', {})
        if airtable_usage.get('usesUpsertPattern'):
            pattern_examples['upsert_pattern'].append(card.get('filePath', ''))
        if airtable_usage.get('usesPaginationLoop'):
            pattern_examples['pagination_pattern'].append(card.get('filePath', ''))

        triggers = card.get('triggers', [])
        if any('webhook' in t.get('type', '').lower() for t in triggers):
            pattern_examples['event_to_airtable'].append(card.get('filePath', ''))

    by_pattern = []
    for pattern_id, examples in pattern_examples.items():
        by_pattern.append({
            'id': pattern_id,
            'count': len(examples),
            'examples': examples[:3]
        })

    # Group by use case tag
    by_use_case = defaultdict(list)
    for card in cards:
        for tag in card.get('useCaseTags', []):
            by_use_case[tag].append(card.get('filePath', ''))

    use_case_list = []
    for tag, examples in by_use_case.items():
        use_case_list.append({
            'tag': tag,
            'count': len(examples),
            'examples': examples[:3]
        })

    use_case_list.sort(key=lambda x: x['count'], reverse=True)

    # Exemplars
    highest_reliability = []
    best_upsert = []
    ai_enhanced = []

    for card in cards:
        scores = card.get('quality', {}).get('scores', {})
        reliability = scores.get('reliabilityScore', 0)
        upsert_score = scores.get('upsertScore', 0)

        filepath = card.get('filePath', '')

        if reliability >= 80:
            highest_reliability.append({'file': filepath, 'score': reliability})

        if upsert_score >= 80:
            best_upsert.append({'file': filepath, 'score': upsert_score})

        if 'ai-powered' in card.get('useCaseTags', []):
            ai_enhanced.append({'file': filepath})

    highest_reliability.sort(key=lambda x: x['score'], reverse=True)
    best_upsert.sort(key=lambda x: x['score'], reverse=True)

    # Count categories
    unique_categories = len(set(card.get('category', 'Other') for card in cards))

    return {
        "generatedAt": datetime.utcnow().isoformat() + "Z",
        "totals": {
            "workflows": len(cards),
            "categories": unique_categories
        },
        "byCategory": category_list,
        "byPattern": by_pattern,
        "byUseCase": use_case_list[:20],  # Top 20 use cases
        "exemplars": {
            "highestReliability": highest_reliability[:5],
            "bestUpsert": best_upsert[:5],
            "aiEnhanced": ai_enhanced[:10]
        }
    }


def main():
    """Main transformation process."""

    base_path = Path("/home/user/n8n-master-workflows")

    # Load input files
    print("Loading input files...")
    cards = load_jsonl(base_path / "workflow_cards.jsonl")
    corpus_summary = load_json(base_path / "corpus_summary.json")
    patterns = load_jsonl(base_path / "pattern_cards.jsonl")

    print(f"Loaded {len(cards)} workflow cards")

    # Transform each workflow card
    print("Transforming workflow cards...")
    descriptions = []
    for i, card in enumerate(cards, 1):
        if i % 50 == 0:
            print(f"  Processed {i}/{len(cards)} workflows...")
        desc = transform_workflow_card(card)
        descriptions.append(desc)

    # Write workflow descriptions
    print("Writing workflow_descriptions.jsonl...")
    output_path = base_path / "workflow_descriptions.jsonl"
    with open(output_path, 'w', encoding='utf-8') as f:
        for desc in descriptions:
            f.write(json.dumps(desc, ensure_ascii=False) + '\n')

    # Generate catalog
    print("Generating catalog.json...")
    catalog = generate_catalog(cards, descriptions)
    catalog_path = base_path / "catalog.json"
    with open(catalog_path, 'w', encoding='utf-8') as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Generated {len(descriptions)} workflow descriptions")
    print(f"✓ Output: {output_path}")
    print(f"✓ Catalog: {catalog_path}")
    print(f"\nCatalog summary:")
    print(f"  - {catalog['totals']['workflows']} workflows")
    print(f"  - {catalog['totals']['categories']} categories")
    print(f"  - {len(catalog['byPattern'])} patterns identified")
    print(f"  - {len(catalog['byUseCase'])} use case tags")


if __name__ == "__main__":
    main()
