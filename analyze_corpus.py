#!/usr/bin/env python3
"""
Corpus analyzer for n8n workflow cards.
Analyzes 295 workflow cards and generates comprehensive summary statistics.
"""

import json
from collections import defaultdict, Counter
from typing import Dict, List, Any
import re

def parse_workflow_cards(file_path: str) -> List[Dict[str, Any]]:
    """Parse all workflow cards from JSONL file."""
    workflows = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                workflows.append(json.loads(line))
    return workflows

def analyze_corpus(workflows: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze the entire corpus and calculate statistics."""

    # Initialize counters
    total_workflows = len(workflows)
    airtable_workflows = 0
    node_counts = {"airtable": 0, "airtableTrigger": 0, "airtableTool": 0}
    all_integrations = []
    categories = Counter()
    operations = Counter()
    triggers = Counter()
    pattern_counter = Counter()

    # Config stats trackers
    typecast_count = 0
    matching_columns_count = 0
    filter_by_formula_count = 0
    wait_backoff_count = 0
    pagination_loop_count = 0
    hardcoded_ids_count = 0

    # Anti-patterns
    legacy_append_count = 0
    blind_update_count = 0
    no_dedupe_before_create_count = 0

    # For exemplars
    high_quality_workflows = []

    # Table archetypes
    table_models = []

    for wf in workflows:
        # Check if Airtable workflow
        nodes = wf.get('nodes', {})
        airtable_node = nodes.get('airtable', {})
        total_airtable = airtable_node.get('count', 0)

        has_airtable = total_airtable > 0
        if has_airtable:
            airtable_workflows += 1

        # Node counts
        node_counts['airtable'] += airtable_node.get('count', 0)
        node_counts['airtableTrigger'] += nodes.get('airtableTrigger', {}).get('count', 0)
        node_counts['airtableTool'] += nodes.get('airtableTool', {}).get('count', 0)

        # Integrations
        integrations = nodes.get('integrations', [])
        # Clean integration names
        clean_integrations = []
        for integ in integrations:
            # Extract readable name from node package name
            if '.' in integ:
                name = integ.split('.')[-1]
            else:
                name = integ
            # Capitalize
            name = name.replace('trigger', '').replace('Trigger', '').strip()
            if name:
                clean_integrations.append(name.capitalize())
        all_integrations.extend(clean_integrations)

        # Categories
        category = wf.get('category', 'Unknown')
        categories[category] += 1

        # Operations
        ops = airtable_node.get('operations', [])
        for op in ops:
            operations[op] += 1

        # Triggers
        trigger_list = wf.get('triggers', [])
        for trigger in trigger_list:
            trigger_type = trigger.get('type', 'Unknown')
            # Clean trigger type
            if '.' in trigger_type:
                trigger_type = trigger_type.split('.')[-1]
            triggers[trigger_type] += 1

        # Patterns from dataFlow.pattern
        data_flow = wf.get('dataFlow', {})
        pattern = data_flow.get('pattern', '')
        if pattern:
            pattern_counter[pattern] += 1

        # Use case tags can also indicate patterns
        use_case_tags = wf.get('useCaseTags', [])
        for tag in use_case_tags:
            pattern_counter[tag] += 1

        # Config stats (for Airtable workflows)
        if has_airtable:
            airtable_usage = wf.get('airtableUsage', {})

            # Typecast - check if used in any operation
            column_mapping_modes = airtable_usage.get('columnMappingMode', [])
            if 'automatic' in column_mapping_modes or 'typecast' in str(airtable_usage).lower():
                typecast_count += 1

            # Matching columns
            matching_columns = airtable_usage.get('matchingColumnsExamples', [])
            if matching_columns and len(matching_columns) > 0:
                matching_columns_count += 1

            # Filter by formula
            filter_formulas = airtable_usage.get('filterByFormulaExamples', [])
            if filter_formulas and len(filter_formulas) > 0:
                filter_by_formula_count += 1

            # Wait or backoff
            if airtable_usage.get('usesWaitOrBackoff', False):
                wait_backoff_count += 1

            # Pagination loop
            if airtable_usage.get('usesPaginationLoop', False):
                pagination_loop_count += 1

            # Hardcoded IDs
            bases = airtable_usage.get('bases', [])
            tables = airtable_usage.get('tables', [])
            if (bases and any(b for b in bases if b.startswith('app'))) or \
               (tables and any(t for t in tables if t.startswith('tbl'))):
                hardcoded_ids_count += 1

            # Anti-patterns
            if not airtable_usage.get('usesUpsertPattern', False) and 'update' in ops:
                blind_update_count += 1

            if not airtable_usage.get('usesDedupBeforeCreate', False) and 'create' in ops:
                no_dedupe_before_create_count += 1

        # Table models
        table_model_hint = wf.get('tableModelsHint', [])
        if isinstance(table_model_hint, list):
            table_models.extend(table_model_hint)
        elif table_model_hint:
            table_models.append(table_model_hint)

        # Collect high quality workflows for exemplars
        quality = wf.get('quality', {})
        scores = quality.get('scores', {})
        # Calculate average quality score
        score_values = [scores.get('upsertScore', 0),
                       scores.get('reliabilityScore', 0),
                       scores.get('maintainabilityScore', 0)]
        avg_score = sum(score_values) / len(score_values) if score_values else 0

        if avg_score >= 60:
            high_quality_workflows.append({
                'file': wf.get('filePath', ''),
                'name': wf.get('title', ''),
                'qualityScore': avg_score,
                'pattern': pattern,
                'useCaseTags': use_case_tags,
                'summary': data_flow.get('sketch', ''),
                'operations': ops,
                'scores': scores,
                'airtableUsage': airtable_usage
            })

    # Calculate percentages
    def calc_pct(count, total):
        return round((count / total * 100), 2) if total > 0 else 0

    # Build distributions
    by_category = [{"name": cat, "count": count} for cat, count in categories.most_common()]
    by_operation = [{"op": op, "pct": calc_pct(count, airtable_workflows)}
                    for op, count in operations.most_common()]
    by_trigger = [{"type": trig, "pct": calc_pct(count, total_workflows)}
                  for trig, count in triggers.most_common()]

    # Patterns - identify main patterns with percentages
    patterns = []

    # Event to Airtable pattern
    event_to_airtable = sum(1 for wf in workflows if
                           'airtable' in wf.get('dataFlow', {}).get('pattern', '').lower() and
                           any(t for t in wf.get('triggers', [])
                               if 'webhook' in t.get('type', '').lower() or
                                  'form' in t.get('type', '').lower()))
    if event_to_airtable >= 3:
        patterns.append({
            "id": "event_to_airtable",
            "label": "Event/Webhook to Airtable Storage",
            "pct": calc_pct(event_to_airtable, total_workflows)
        })

    # Airtable to external
    airtable_to_external = sum(1 for wf in workflows if
                               wf.get('nodes', {}).get('airtableTrigger', {}).get('count', 0) > 0 and
                               len(wf.get('nodes', {}).get('integrations', [])) > 2)
    if airtable_to_external >= 3:
        patterns.append({
            "id": "airtable_to_external",
            "label": "Airtable Trigger to External Service",
            "pct": calc_pct(airtable_to_external, total_workflows)
        })

    # Bidirectional sync
    bidirectional_sync = sum(1 for wf in workflows if
                            'sync' in wf.get('dataFlow', {}).get('pattern', '').lower() or
                            'sync' in wf.get('useCaseTags', []))
    if bidirectional_sync >= 3:
        patterns.append({
            "id": "bidirectional_sync",
            "label": "Bidirectional Data Synchronization",
            "pct": calc_pct(bidirectional_sync, total_workflows)
        })

    # Lookup/Enrich/Upsert pattern
    lookup_enrich = sum(1 for wf in workflows if
                       wf.get('airtableUsage', {}).get('usesUpsertPattern', False) or
                       'enrich' in wf.get('useCaseTags', []) or
                       'lookup' in wf.get('useCaseTags', []))
    if lookup_enrich >= 3:
        patterns.append({
            "id": "lookup_enrich_upsert",
            "label": "Lookup/Enrich/Upsert Pattern",
            "pct": calc_pct(lookup_enrich, total_workflows)
        })

    # Config stats
    config_stats = {
        "typecastUsedPct": calc_pct(typecast_count, airtable_workflows),
        "usesMatchingColumnsPct": calc_pct(matching_columns_count, airtable_workflows),
        "usesFilterByFormulaPct": calc_pct(filter_by_formula_count, airtable_workflows),
        "usesWaitOrBackoffPct": calc_pct(wait_backoff_count, airtable_workflows),
        "usesPaginationLoopPct": calc_pct(pagination_loop_count, airtable_workflows),
        "hardcodedIdsPct": calc_pct(hardcoded_ids_count, airtable_workflows)
    }

    # Anti-patterns
    anti_patterns_list = []
    if legacy_append_count > 0:
        anti_patterns_list.append({"id": "legacy-append", "count": legacy_append_count})
    if blind_update_count > 0:
        anti_patterns_list.append({"id": "blind-update", "count": blind_update_count})
    if no_dedupe_before_create_count > 0:
        anti_patterns_list.append({"id": "no-dedupe-before-create", "count": no_dedupe_before_create_count})

    # Top integrations
    integration_counts = Counter(all_integrations)
    top_integrations = [{"name": name, "count": count}
                       for name, count in integration_counts.most_common(15)]

    # Table archetypes - extract common patterns
    archetype_keywords = Counter()
    for model in table_models:
        if isinstance(model, str):
            words = re.findall(r'\b\w+\b', model.lower())
            common_types = ['contacts', 'leads', 'users', 'transactions', 'events',
                           'messages', 'submissions', 'engagement', 'points', 'records',
                           'companies', 'deals', 'tasks', 'tickets', 'orders', 'customers',
                           'products', 'invoices', 'payments', 'campaigns']
            for word in words:
                if word in common_types:
                    archetype_keywords[word] += 1

    table_archetypes = [archetype for archetype, count in archetype_keywords.most_common(10)
                       if count >= 3]

    # Select exemplars - diverse, high quality workflows
    exemplars = []
    high_quality_workflows.sort(key=lambda x: x['qualityScore'], reverse=True)

    # Select diverse exemplars
    selected_patterns = set()
    for wf in high_quality_workflows:
        if len(exemplars) >= 10:
            break

        # Determine why this is exemplary
        reasons = []
        ops = wf.get('operations', [])
        usage = wf.get('airtableUsage', {})
        scores = wf.get('scores', {})

        # Check for upsert pattern
        if usage.get('usesUpsertPattern') and 'upsert' not in selected_patterns:
            reasons.append("robust upsert pattern")
            selected_patterns.add('upsert')
        # Check for create operations
        elif 'create' in ops and 'create' not in selected_patterns:
            if usage.get('usesDedupBeforeCreate'):
                reasons.append("clean CREATE with deduplication")
            else:
                reasons.append("clean CREATE mapping")
            selected_patterns.add('create')
        # Check for update operations
        elif 'update' in ops and 'update' not in selected_patterns:
            reasons.append("conditional update logic")
            selected_patterns.add('update')
        # Check for search operations
        elif 'search' in ops and 'search' not in selected_patterns:
            reasons.append("lookup and search pattern")
            selected_patterns.add('search')
        # Check for pagination
        elif usage.get('usesPaginationLoop') and 'pagination' not in selected_patterns:
            reasons.append("pagination loop implementation")
            selected_patterns.add('pagination')
        # Check for filter by formula
        elif usage.get('filterByFormulaExamples') and len(usage['filterByFormulaExamples']) > 0 and 'filter' not in selected_patterns:
            reasons.append("advanced filtering with formulas")
            selected_patterns.add('filter')

        # High scores
        if scores.get('reliabilityScore', 0) >= 80 and 'reliability' not in selected_patterns:
            reasons.append(f"high reliability (score: {scores['reliabilityScore']})")
            selected_patterns.add('reliability')
        elif scores.get('upsertScore', 0) >= 80 and 'upsert-score' not in selected_patterns:
            reasons.append(f"excellent upsert implementation (score: {scores['upsertScore']})")
            selected_patterns.add('upsert-score')

        if reasons or len(exemplars) < 5:
            if not reasons:
                reasons.append(f"high quality implementation (avg score: {int(wf['qualityScore'])})")

            exemplars.append({
                "file": wf['file'],
                "why": ", ".join(reasons)
            })

    # Build final summary
    summary = {
        "totals": {
            "workflows": total_workflows,
            "airtableWorkflows": airtable_workflows,
            "nodeTypes": node_counts,
            "integrationsUnique": len(integration_counts)
        },
        "distributions": {
            "byCategory": by_category,
            "byOperation": by_operation,
            "byTrigger": by_trigger
        },
        "patterns": patterns,
        "configStats": config_stats,
        "antiPatterns": anti_patterns_list,
        "topIntegrations": top_integrations,
        "tableArchetypes": table_archetypes,
        "exemplars": exemplars
    }

    return summary

def identify_pattern_cards(workflows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Identify recurring patterns and create recipe cards."""

    pattern_cards = []

    # Track pattern occurrences
    pattern_tracker = defaultdict(lambda: {
        'count': 0,
        'examples': [],
        'steps': set(),
        'benefits': set()
    })

    for wf in workflows:
        nodes = wf.get('nodes', {})
        airtable_node = nodes.get('airtable', {})
        ops = airtable_node.get('operations', [])
        pattern = wf.get('dataFlow', {}).get('pattern', '')
        tags = wf.get('useCaseTags', [])
        name = wf.get('title', '')
        airtable_usage = wf.get('airtableUsage', {})
        integrations = nodes.get('integrations', [])

        # Pattern 1: Upsert by unique key (Search → IF → Update/Create)
        if airtable_usage.get('usesUpsertPattern', False):
            pattern_tracker['upsert_pattern']['count'] += 1
            pattern_tracker['upsert_pattern']['examples'].append(name)
            pattern_tracker['upsert_pattern']['steps'].update([
                "Search Airtable for existing record by unique key",
                "Check if record exists using IF node",
                "Update if found, Create if not found"
            ])
            pattern_tracker['upsert_pattern']['benefits'].update([
                "Prevents duplicate records",
                "Maintains data consistency",
                "Idempotent operation"
            ])

        # Pattern 2: Pagination loops
        if airtable_usage.get('usesPaginationLoop', False):
            pattern_tracker['pagination_pattern']['count'] += 1
            pattern_tracker['pagination_pattern']['examples'].append(name)
            pattern_tracker['pagination_pattern']['steps'].update([
                "Use SplitInBatches node to process records in chunks",
                "Execute List or Search operations with pagination",
                "Loop until all records are processed"
            ])
            pattern_tracker['pagination_pattern']['benefits'].update([
                "Handles large datasets efficiently",
                "Prevents API rate limiting",
                "Reduces memory usage"
            ])

        # Pattern 3: Form submission storage
        trigger_types = [t.get('type', '') for t in wf.get('triggers', [])]
        has_webhook = any('webhook' in t.lower() or 'form' in t.lower() for t in trigger_types)
        if has_webhook and 'create' in ops:
            pattern_tracker['form_storage']['count'] += 1
            pattern_tracker['form_storage']['examples'].append(name)
            pattern_tracker['form_storage']['steps'].update([
                "Receive webhook from form submission",
                "Transform and validate data",
                "Create new record in Airtable"
            ])
            pattern_tracker['form_storage']['benefits'].update([
                "Centralized data collection",
                "Automated data entry",
                "Real-time storage"
            ])

        # Pattern 4: Deduplication before create
        if airtable_usage.get('usesDedupBeforeCreate', False):
            pattern_tracker['dedupe_pattern']['count'] += 1
            pattern_tracker['dedupe_pattern']['examples'].append(name)
            pattern_tracker['dedupe_pattern']['steps'].update([
                "Search for duplicate records before creating",
                "Use unique identifiers (email, ID, etc.)",
                "Only create if no duplicate found"
            ])
            pattern_tracker['dedupe_pattern']['benefits'].update([
                "Prevents duplicate entries",
                "Maintains data quality",
                "Ensures unique constraints"
            ])

        # Pattern 5: Airtable trigger to external service
        if nodes.get('airtableTrigger', {}).get('count', 0) > 0:
            pattern_tracker['trigger_external']['count'] += 1
            pattern_tracker['trigger_external']['examples'].append(name)
            pattern_tracker['trigger_external']['steps'].update([
                "Monitor Airtable for new/updated records",
                "Transform data as needed",
                "Send to external service or notification"
            ])
            pattern_tracker['trigger_external']['benefits'].update([
                "Real-time automation",
                "Event-driven architecture",
                "Reduces manual work"
            ])

        # Pattern 6: WhatsApp/Telegram engagement tracking
        has_messaging = any('whatsapp' in i.lower() or 'telegram' in i.lower()
                          for i in integrations)
        if has_messaging and 'update' in ops:
            pattern_tracker['messaging_engagement']['count'] += 1
            pattern_tracker['messaging_engagement']['examples'].append(name)
            pattern_tracker['messaging_engagement']['steps'].update([
                "Receive message from messaging platform",
                "Extract user identifier and message data",
                "Update engagement metrics in Airtable"
            ])
            pattern_tracker['messaging_engagement']['benefits'].update([
                "Track user engagement",
                "Build interaction history",
                "Enable personalized responses"
            ])

        # Pattern 7: AI enhancement pattern
        has_ai = any('openai' in i.lower() or 'ai' in i.lower() or 'gpt' in i.lower()
                    for i in integrations)
        if has_ai and 'update' in ops:
            pattern_tracker['ai_enhancement']['count'] += 1
            pattern_tracker['ai_enhancement']['examples'].append(name)
            pattern_tracker['ai_enhancement']['steps'].update([
                "Read data from Airtable",
                "Process with AI/LLM",
                "Update record with AI-generated content"
            ])
            pattern_tracker['ai_enhancement']['benefits'].update([
                "Automated content generation",
                "Data enrichment with AI",
                "Intelligent processing"
            ])

        # Pattern 8: Scheduled batch processing
        has_schedule = any('schedule' in t.lower() or 'cron' in t.lower()
                          for t in trigger_types)
        if has_schedule and ('list' in ops or 'search' in ops):
            pattern_tracker['scheduled_batch']['count'] += 1
            pattern_tracker['scheduled_batch']['examples'].append(name)
            pattern_tracker['scheduled_batch']['steps'].update([
                "Trigger workflow on schedule (daily, hourly, etc.)",
                "Fetch records from Airtable",
                "Process and update in batches"
            ])
            pattern_tracker['scheduled_batch']['benefits'].update([
                "Automated recurring tasks",
                "Batch processing efficiency",
                "Timely data updates"
            ])

        # Pattern 9: Filter by formula advanced queries
        filter_formulas = airtable_usage.get('filterByFormulaExamples', [])
        if filter_formulas and len(filter_formulas) > 0:
            pattern_tracker['filter_formula']['count'] += 1
            pattern_tracker['filter_formula']['examples'].append(name)
            pattern_tracker['filter_formula']['steps'].update([
                "Define filter formula to target specific records",
                "Use Airtable formula syntax for complex conditions",
                "Process only matching records"
            ])
            pattern_tracker['filter_formula']['benefits'].update([
                "Precise record selection",
                "Reduces processing overhead",
                "Leverages Airtable's formula engine"
            ])

        # Pattern 10: Multi-table workflows
        tables = airtable_usage.get('tables', [])
        if len(tables) >= 2:
            pattern_tracker['multi_table']['count'] += 1
            pattern_tracker['multi_table']['examples'].append(name)
            pattern_tracker['multi_table']['steps'].update([
                "Coordinate operations across multiple tables",
                "Maintain relationships between tables",
                "Update linked records appropriately"
            ])
            pattern_tracker['multi_table']['benefits'].update([
                "Complex data relationships",
                "Normalized data structure",
                "Coordinated updates"
            ])

    # Create recipe cards for patterns with 3+ occurrences
    pattern_definitions = {
        'upsert_pattern': {
            'label': 'Upsert by Unique Key',
            'applicability': 'Airtable'
        },
        'pagination_pattern': {
            'label': 'Pagination Loop for Large Datasets',
            'applicability': 'Airtable'
        },
        'form_storage': {
            'label': 'Form Submission to Airtable Storage',
            'applicability': 'Airtable'
        },
        'dedupe_pattern': {
            'label': 'Deduplication Before Create',
            'applicability': 'Airtable'
        },
        'trigger_external': {
            'label': 'Airtable Trigger to External Service',
            'applicability': 'Airtable'
        },
        'messaging_engagement': {
            'label': 'Messaging Platform Engagement Tracking',
            'applicability': 'Airtable'
        },
        'ai_enhancement': {
            'label': 'AI-Powered Data Enhancement',
            'applicability': 'Airtable'
        },
        'scheduled_batch': {
            'label': 'Scheduled Batch Processing',
            'applicability': 'Airtable'
        },
        'filter_formula': {
            'label': 'Advanced Filtering with Formulas',
            'applicability': 'Airtable'
        },
        'multi_table': {
            'label': 'Multi-Table Coordinated Operations',
            'applicability': 'Airtable'
        }
    }

    for pattern_id, data in pattern_tracker.items():
        if data['count'] >= 3:
            card = {
                "id": pattern_id,
                "label": pattern_definitions[pattern_id]['label'],
                "applicability": pattern_definitions[pattern_id]['applicability'],
                "steps": list(data['steps']),
                "qualityBenefits": list(data['benefits']),
                "example": data['examples'][0] if data['examples'] else "",
                "occurrences": data['count']
            }
            pattern_cards.append(card)

    return pattern_cards

def main():
    """Main execution function."""
    input_file = '/home/user/n8n-master-workflows/workflow_cards.jsonl'
    summary_output = '/home/user/n8n-master-workflows/corpus_summary.json'
    patterns_output = '/home/user/n8n-master-workflows/pattern_cards.jsonl'

    print("Reading workflow cards...")
    workflows = parse_workflow_cards(input_file)
    print(f"Loaded {len(workflows)} workflows")

    print("Analyzing corpus...")
    summary = analyze_corpus(workflows)

    print("Identifying pattern cards...")
    pattern_cards = identify_pattern_cards(workflows)

    print("Writing corpus_summary.json...")
    with open(summary_output, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print("Writing pattern_cards.jsonl...")
    with open(patterns_output, 'w', encoding='utf-8') as f:
        for card in pattern_cards:
            f.write(json.dumps(card, ensure_ascii=False) + '\n')

    print(f"\n✓ Corpus analysis complete!")
    print(f"✓ Summary: {summary_output}")
    print(f"✓ Patterns: {patterns_output}")
    print(f"\nStats:")
    print(f"  - Total workflows: {summary['totals']['workflows']}")
    print(f"  - Airtable workflows: {summary['totals']['airtableWorkflows']}")
    print(f"  - Unique integrations: {summary['totals']['integrationsUnique']}")
    print(f"  - Pattern cards generated: {len(pattern_cards)}")

if __name__ == '__main__':
    main()
