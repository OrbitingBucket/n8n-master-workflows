#!/usr/bin/env python3
import json
import re
from typing import Dict, List, Any, Set

# Controlled vocabularies
VALID_TRIGGER_TYPES = {
    "webhook", "schedule", "manual", "airtableTrigger", "chat", "form",
    "gmail", "whatsapp", "telegram", "slack", "discord"
}

VALID_AIRTABLE_OPS = {
    "create", "append", "search", "list", "read", "update", "delete", "upsert", "getSchema"
}

VALID_USE_CASE_TAGS = {
    "lead_generation", "engagement_tracking", "data_collection", "reporting",
    "chatbot", "content_mgmt", "order_tracking", "bidirectional_sync",
    "lookup_enrich_upsert", "ai_enhanced", "crm", "social_media", "marketing",
    "sales", "support", "hr", "finance", "automation", "form_submission",
    "email_automation"
}

# Tag normalization mappings
TAG_SYNONYMS = {
    "lead generation": "lead_generation",
    "leadgeneration": "lead_generation",
    "leads": "lead_generation",
    "engagement tracking": "engagement_tracking",
    "engagement": "engagement_tracking",
    "data collection": "data_collection",
    "datacollection": "data_collection",
    "collection": "data_collection",
    "report": "reporting",
    "reports": "reporting",
    "chat bot": "chatbot",
    "chat": "chatbot",
    "content management": "content_mgmt",
    "content": "content_mgmt",
    "order tracking": "order_tracking",
    "orders": "order_tracking",
    "bidirectional sync": "bidirectional_sync",
    "sync": "bidirectional_sync",
    "two-way sync": "bidirectional_sync",
    "lookup enrich upsert": "lookup_enrich_upsert",
    "lookup": "lookup_enrich_upsert",
    "enrich": "lookup_enrich_upsert",
    "upsert": "lookup_enrich_upsert",
    "ai enhanced": "ai_enhanced",
    "ai": "ai_enhanced",
    "customer relationship management": "crm",
    "social": "social_media",
    "form submission": "form_submission",
    "forms": "form_submission",
    "email automation": "email_automation",
    "email": "email_automation"
}

def to_kebab_case(text: str) -> str:
    """Convert text to kebab-case"""
    # Remove special characters, keep alphanumeric and spaces
    text = re.sub(r'[^\w\s-]', '', text)
    # Replace spaces and underscores with hyphens
    text = re.sub(r'[-\s]+', '-', text)
    # Convert to lowercase
    return text.lower().strip('-')

def truncate_with_ellipsis(text: str, max_length: int) -> str:
    """Truncate text to max_length with ellipsis if needed"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

def normalize_trigger_type(trigger_type: str) -> str:
    """Normalize trigger type to controlled vocabulary"""
    trigger_lower = trigger_type.lower().strip()

    # Direct match
    if trigger_lower in VALID_TRIGGER_TYPES:
        return trigger_lower

    # Try to map common variations
    mappings = {
        "cron": "schedule",
        "timer": "schedule",
        "http": "webhook",
        "httprequest": "webhook",
        "airtable trigger": "airtableTrigger",
        "airtable": "airtableTrigger",
        "chatbot": "chat",
        "formtrigger": "form",
        "email": "gmail"
    }

    if trigger_lower in mappings:
        return mappings[trigger_lower]

    # Check if any valid trigger is contained in the type
    for valid in VALID_TRIGGER_TYPES:
        if valid in trigger_lower:
            return valid

    # Default to manual if can't determine
    return "manual"

def normalize_airtable_operations(operations: List[str]) -> List[str]:
    """Normalize Airtable operations to controlled vocabulary"""
    normalized = []
    for op in operations:
        op_lower = op.lower().strip()
        if op_lower in VALID_AIRTABLE_OPS:
            normalized.append(op_lower)
        else:
            # Try to map variations
            if "get" in op_lower and "schema" in op_lower:
                normalized.append("getSchema")
            elif "upsert" in op_lower:
                normalized.append("upsert")
            elif "append" in op_lower:
                normalized.append("append")
            elif "create" in op_lower or "insert" in op_lower:
                normalized.append("create")
            elif "update" in op_lower or "modify" in op_lower:
                normalized.append("update")
            elif "delete" in op_lower or "remove" in op_lower:
                normalized.append("delete")
            elif "search" in op_lower or "find" in op_lower:
                normalized.append("search")
            elif "list" in op_lower:
                normalized.append("list")
            elif "read" in op_lower or "get" in op_lower:
                normalized.append("read")

    # Remove duplicates while preserving order
    seen = set()
    result = []
    for op in normalized:
        if op not in seen:
            seen.add(op)
            result.append(op)

    return result

def normalize_category(category: str) -> str:
    """Normalize category with underscores and proper casing"""
    # Replace spaces and hyphens with underscores
    normalized = category.replace(' ', '_').replace('-', '_')
    # Convert to lowercase
    normalized = normalized.lower()
    # Remove any special characters
    normalized = re.sub(r'[^\w_]', '', normalized)
    return normalized

def normalize_use_case_tags(tags: List[str]) -> List[str]:
    """Normalize use case tags to controlled vocabulary"""
    normalized = set()

    for tag in tags:
        tag_lower = tag.lower().strip()

        # Replace spaces and hyphens with underscores
        tag_normalized = tag_lower.replace(' ', '_').replace('-', '_')

        # Direct match
        if tag_normalized in VALID_USE_CASE_TAGS:
            normalized.add(tag_normalized)
        # Check synonyms
        elif tag_lower in TAG_SYNONYMS:
            normalized.add(TAG_SYNONYMS[tag_lower])
        elif tag_normalized in TAG_SYNONYMS:
            normalized.add(TAG_SYNONYMS[tag_normalized])
        else:
            # Try to find a match in valid tags
            found = False
            for valid_tag in VALID_USE_CASE_TAGS:
                if valid_tag in tag_normalized or tag_normalized in valid_tag:
                    normalized.add(valid_tag)
                    found = True
                    break

            # If still not found, keep the normalized version
            if not found and tag_normalized:
                # Check if it's close to any valid tag
                best_match = None
                for valid_tag in VALID_USE_CASE_TAGS:
                    if valid_tag.replace('_', '') in tag_normalized.replace('_', ''):
                        best_match = valid_tag
                        break

                if best_match:
                    normalized.add(best_match)

    return sorted(list(normalized))

def generate_ir_plan(workflow: Dict[str, Any]) -> str:
    """Generate IR plan representation"""
    trigger = workflow.get("trigger", {})
    trigger_type = trigger.get("type", "manual")

    data_flow = workflow.get("dataFlow", "")
    airtable = workflow.get("airtable", {})
    operations = airtable.get("operations", [])

    # Start with trigger
    ir_parts = [f"trigger:{trigger_type}"]

    # Parse dataFlow to understand the workflow
    if operations:
        # Build operation chain from operations and dataFlow
        if "search" in operations:
            ir_parts.append("airtable.search()")

        # Check for conditional logic in dataFlow
        has_conditional = any(word in data_flow.lower() for word in ["if", "check", "condition", "found", "exist"])

        if has_conditional:
            if "update" in operations and "create" in operations:
                ir_parts.append("if(found) airtable.update() else airtable.create()")
            elif "update" in operations:
                ir_parts.append("if(found) airtable.update()")
            elif "create" in operations:
                ir_parts.append("if(notFound) airtable.create()")
        else:
            # Add remaining operations
            for op in operations:
                if op not in ["search"]:  # Already added search
                    ir_parts.append(f"airtable.{op}()")

    return " -> ".join(ir_parts)

def ensure_airtable_pat_in_checklist(checklist: List[str]) -> List[str]:
    """Ensure first item mentions Airtable PAT scopes"""
    if not checklist:
        return ["Configure Airtable Personal Access Token with required scopes"]

    # Check if first item mentions Airtable and PAT/token/credentials
    first_item = checklist[0].lower()
    has_airtable = "airtable" in first_item
    has_pat = any(word in first_item for word in ["pat", "token", "credential", "api key", "access"])

    if not (has_airtable and has_pat):
        # Prepend the required item
        return ["Configure Airtable Personal Access Token with required scopes"] + checklist

    return checklist

def normalize_workflow(workflow: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize a single workflow according to schema and rules"""
    normalized = {}

    # Required fields
    normalized["filePath"] = workflow.get("filePath", "")

    # Title (max 70 chars)
    title = workflow.get("title", "")
    normalized["title"] = truncate_with_ellipsis(title, 70)

    # OneLiner (max 160 chars)
    one_liner = workflow.get("oneLiner", "")
    normalized["oneLiner"] = truncate_with_ellipsis(one_liner, 160)

    # WhenToUse (optional, max 3 items)
    when_to_use = workflow.get("whenToUse", [])
    if when_to_use:
        normalized["whenToUse"] = when_to_use[:3]

    # Trigger
    trigger = workflow.get("trigger", {})
    normalized["trigger"] = {
        "type": normalize_trigger_type(trigger.get("type", "manual"))
    }
    if "details" in trigger:
        normalized["trigger"]["details"] = trigger["details"]

    # DataFlow (max 120 chars)
    data_flow = workflow.get("dataFlow", "")
    normalized["dataFlow"] = truncate_with_ellipsis(data_flow, 120)

    # Airtable
    airtable = workflow.get("airtable", {})
    normalized["airtable"] = {
        "tables": airtable.get("tables", "hardcoded"),
        "operations": normalize_airtable_operations(airtable.get("operations", [])),
        "upsert": airtable.get("upsert", False),
        "pagination": airtable.get("pagination", False),
        "rateLimiting": airtable.get("rateLimiting", False)
    }

    if "filterByFormulaExamples" in airtable:
        normalized["airtable"]["filterByFormulaExamples"] = airtable["filterByFormulaExamples"]

    # Integrations (optional)
    if "integrations" in workflow:
        normalized["integrations"] = workflow["integrations"]

    # SetupChecklist (optional, but ensure Airtable PAT)
    setup_checklist = workflow.get("setupChecklist", [])
    if setup_checklist:
        normalized["setupChecklist"] = ensure_airtable_pat_in_checklist(setup_checklist)

    # QualityNotes
    quality_notes = workflow.get("qualityNotes", {})
    scores = quality_notes.get("scores", {})

    reliability = scores.get("reliability", 0)
    maintainability = scores.get("maintainability", 0)
    security = scores.get("security", 0)
    overall = round((reliability + maintainability + security) / 3)

    normalized["qualityNotes"] = {
        "lints": quality_notes.get("lints", []),
        "scores": {
            "reliability": reliability,
            "maintainability": maintainability,
            "security": security,
            "overall": overall
        }
    }

    # Snippets (optional)
    if "snippets" in workflow:
        normalized["snippets"] = workflow["snippets"]

    # Category
    category = workflow.get("category", "")
    normalized["category"] = normalize_category(category)

    # UseCaseTags (deduplicate and normalize)
    use_case_tags = workflow.get("useCaseTags", [])
    normalized["useCaseTags"] = normalize_use_case_tags(use_case_tags)

    # Slug (derived from title)
    normalized["slug"] = to_kebab_case(normalized["title"])

    # IR Plan
    normalized["irPlan"] = generate_ir_plan(normalized)

    return normalized

def main():
    input_file = "/home/user/n8n-master-workflows/workflow_descriptions.jsonl"
    output_file = "/home/user/n8n-master-workflows/workflow_descriptions.normalized.jsonl"
    catalog_file = "/home/user/n8n-master-workflows/catalog.index.json"

    normalized_workflows = []

    # Read and normalize each workflow
    with open(input_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue

            try:
                workflow = json.loads(line)
                normalized = normalize_workflow(workflow)
                normalized_workflows.append(normalized)
            except json.JSONDecodeError as e:
                print(f"Error parsing line {line_num}: {e}")
                continue
            except Exception as e:
                print(f"Error normalizing line {line_num}: {e}")
                continue

    # Write normalized JSONL
    with open(output_file, 'w', encoding='utf-8') as f:
        for workflow in normalized_workflows:
            f.write(json.dumps(workflow, separators=(',', ':')) + '\n')

    # Create catalog index
    catalog = []
    for workflow in normalized_workflows:
        catalog.append({
            "slug": workflow["slug"],
            "title": workflow["title"],
            "category": workflow["category"],
            "useCaseTags": workflow["useCaseTags"],
            "overall": workflow["qualityNotes"]["scores"]["overall"],
            "filePath": workflow["filePath"]
        })

    # Sort by overall score descending
    catalog.sort(key=lambda x: x["overall"], reverse=True)

    # Write catalog index (pretty-printed)
    with open(catalog_file, 'w', encoding='utf-8') as f:
        json.dump(catalog, f, indent=2)

    print(f"Processed {len(normalized_workflows)} workflows")
    print(f"Output files:")
    print(f"  - {output_file}")
    print(f"  - {catalog_file}")

if __name__ == "__main__":
    main()
