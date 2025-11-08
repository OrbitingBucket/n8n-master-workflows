#!/usr/bin/env python3
"""
Remediation Planner for n8n Airtable Workflows
Analyzes workflow quality issues and generates concrete, deterministic fix plans.
"""

import json
import sys
from typing import List, Dict, Any, Set
from dataclasses import dataclass, field


@dataclass
class RemediationCard:
    """Structured remediation plan for a workflow."""
    filePath: str
    priority: str  # high | medium | low
    reasons: List[str]
    fixPlan: List[Dict[str, Any]]
    n8nPatches: List[Dict[str, Any]]
    tests: List[str]
    estimatedImpact: Dict[str, str]


class RemediationPlanner:
    """Generates remediation cards for workflows with quality issues."""

    def __init__(self):
        self.workflows_by_path = {}

    def load_data(self, descriptions_path: str, cards_path: str):
        """Load workflow descriptions and cards."""
        print("Loading workflow data...")

        # Load descriptions
        with open(descriptions_path, 'r') as f:
            for line in f:
                if line.strip():
                    workflow = json.loads(line)
                    path = workflow.get('filePath', '')
                    self.workflows_by_path[path] = {
                        'description': workflow,
                        'card': None
                    }

        # Load cards
        with open(cards_path, 'r') as f:
            for line in f:
                if line.strip():
                    card = json.loads(line)
                    path = card.get('filePath', '')
                    if path in self.workflows_by_path:
                        self.workflows_by_path[path]['card'] = card

        print(f"Loaded {len(self.workflows_by_path)} workflows")

    def needs_remediation(self, workflow_data: Dict[str, Any]) -> bool:
        """Check if workflow needs remediation."""
        desc = workflow_data.get('description', {})
        card = workflow_data.get('card', {})

        if not desc:
            return False

        # Check quality notes
        quality_notes = desc.get('qualityNotes', {})
        scores = quality_notes.get('scores', {})
        lints = quality_notes.get('lints', [])

        # Check for lints (excluding just error handling)
        has_quality_lints = any(
            lint.get('id', '') not in ['no_explicit_error_handling_detected', '']
            for lint in lints
        )

        # Check scores
        reliability = scores.get('reliability', 100)
        maintainability = scores.get('maintainability', 100)
        security = scores.get('security', 100)

        low_scores = reliability < 70 or maintainability < 60 or security < 80

        # Check Airtable-specific issues from card
        if card:
            airtable_usage = card.get('airtableUsage', {})
            has_airtable_issues = (
                not airtable_usage.get('usesDedupBeforeCreate', False) or
                not airtable_usage.get('usesPaginationLoop', False)
            )
        else:
            has_airtable_issues = False

        return has_quality_lints or low_scores or has_airtable_issues

    def identify_issues(self, workflow_data: Dict[str, Any]) -> Set[str]:
        """Identify specific issues for a workflow."""
        issues = set()

        desc = workflow_data.get('description', {})
        card = workflow_data.get('card', {})

        if not desc:
            return issues

        # Check quality notes from description
        quality_notes = desc.get('qualityNotes', {})
        scores = quality_notes.get('scores', {})
        lints = quality_notes.get('lints', [])

        # Map lints to issue IDs
        for lint in lints:
            lint_id = lint.get('id', '')
            if 'blind-update' in lint_id or 'blind_update' in lint_id:
                issues.add('blind-update')
            if 'no-dedupe' in lint_id or 'no_dedupe' in lint_id:
                issues.add('no-dedupe-before-create')
            if 'pagination' in lint_id:
                issues.add('missing-pagination')
            if 'hardcoded' in lint_id:
                issues.add('hardcoded-ids')
            if 'typecast' in lint_id:
                issues.add('missing-typecast')

        # Check scores
        reliability = scores.get('reliability', 100)
        maintainability = scores.get('maintainability', 100)
        security = scores.get('security', 100)

        if reliability < 70:
            issues.add('low-reliability')
        if maintainability < 60:
            issues.add('low-maintainability')
        if security < 80:
            issues.add('low-security')

        # Check Airtable usage patterns from card
        if card:
            airtable_usage = card.get('airtableUsage', {})
            operations = airtable_usage.get('operations', {})

            # Check for blind update
            if 'update' in operations and not airtable_usage.get('usesUpsertPattern', False):
                if 'search' not in operations:
                    issues.add('blind-update')

            # Check for missing dedup before create
            if 'create' in operations and not airtable_usage.get('usesDedupBeforeCreate', False):
                issues.add('no-dedupe-before-create')

            # Check for missing pagination
            if ('list' in operations or 'search' in operations) and not airtable_usage.get('usesPaginationLoop', False):
                issues.add('missing-pagination')

            # Check for missing typecast
            if ('create' in operations or 'update' in operations):
                # Heuristic: if reliability < 80, likely missing typecast
                if reliability < 80:
                    issues.add('missing-typecast')

        return issues

    def calculate_priority(self, issues: Set[str]) -> str:
        """Calculate priority based on issues."""
        if any(issue in issues for issue in ['blind-update', 'no-dedupe-before-create', 'low-security']):
            return 'high'
        elif any(issue in issues for issue in ['missing-pagination', 'hardcoded-ids', 'low-reliability']):
            return 'medium'
        else:
            return 'low'

    def generate_fix_plan(self, issues: Set[str], workflow_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate concrete fix steps for identified issues."""
        fix_plan = []

        desc = workflow_data.get('description', {})
        airtable_info = desc.get('airtable', {})
        operations = airtable_info.get('operations', [])

        # Fix blind-update
        if 'blind-update' in issues:
            # Get example filter if available
            filter_examples = airtable_info.get('filterByFormulaExamples', [])
            filter_formula = filter_examples[0] if filter_examples else "RECORD_ID()='{{$json.id}}'"

            fix_plan.append({
                "step": "insert",
                "node": "Airtable",
                "operation": "search",
                "where": "before:update",
                "params": {"filterByFormula": filter_formula}
            })
            fix_plan.append({
                "step": "branch",
                "type": "if",
                "condition": "{{ $json.records.length > 0 }}",
                "then": "update",
                "else": "create"
            })

        # Fix no-dedupe-before-create
        if 'no-dedupe-before-create' in issues and 'blind-update' not in issues:
            filter_examples = airtable_info.get('filterByFormulaExamples', [])
            filter_formula = filter_examples[0] if filter_examples else "RECORD_ID()='{{$json.id}}'"

            fix_plan.append({
                "step": "insert",
                "node": "Airtable",
                "operation": "search",
                "where": "before:create",
                "params": {"filterByFormula": filter_formula}
            })
            fix_plan.append({
                "step": "branch",
                "type": "if",
                "condition": "{{ $json.records.length === 0 }}",
                "then": "create",
                "else": "skip"
            })

        # Fix missing-pagination
        if 'missing-pagination' in issues:
            fix_plan.append({
                "step": "insert",
                "node": "SplitInBatches",
                "size": 50,
                "where": "before:airtable.list"
            })
            fix_plan.append({
                "step": "insert",
                "node": "Wait",
                "ms": 150,
                "where": "after:splitInBatches.loop"
            })
            fix_plan.append({
                "step": "setOption",
                "node": "Airtable(operation=list|search)",
                "option": "limit",
                "value": 100
            })

        # Fix hardcoded-ids
        if 'hardcoded-ids' in issues:
            fix_plan.append({
                "step": "setOption",
                "node": "Airtable",
                "option": "base.__rl.mode",
                "value": "list"
            })
            fix_plan.append({
                "step": "setOption",
                "node": "Airtable",
                "option": "table.__rl.mode",
                "value": "list"
            })

        # Fix missing-typecast
        if 'missing-typecast' in issues:
            fix_plan.append({
                "step": "setOption",
                "node": "Airtable(operation=create|update)",
                "option": "options.typecast",
                "value": True
            })

        # Fix low-reliability
        if 'low-reliability' in issues:
            fix_plan.append({
                "step": "setOption",
                "node": "all",
                "option": "retryOnFail",
                "value": True
            })
            fix_plan.append({
                "step": "setOption",
                "node": "all",
                "option": "maxTries",
                "value": 3
            })

        return fix_plan

    def generate_n8n_patches(self, issues: Set[str], workflow_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate JSON Patch operations for n8n workflow."""
        patches = []

        # For blind-update: Add search node
        if 'blind-update' in issues:
            patches.append({
                "op": "add",
                "path": "/nodes/-",
                "value": {
                    "type": "n8n-nodes-base.airtable",
                    "name": "Search Before Update",
                    "parameters": {
                        "operation": "search",
                        "filterByFormula": "={{$json.searchField}}"
                    }
                }
            })
            patches.append({
                "op": "add",
                "path": "/nodes/-",
                "value": {
                    "type": "n8n-nodes-base.if",
                    "name": "Record Exists?",
                    "parameters": {
                        "conditions": {
                            "number": [{
                                "value1": "={{$json.records.length}}",
                                "operation": "larger",
                                "value2": 0
                            }]
                        }
                    }
                }
            })

        # For no-dedupe: Add search node
        if 'no-dedupe-before-create' in issues and 'blind-update' not in issues:
            patches.append({
                "op": "add",
                "path": "/nodes/-",
                "value": {
                    "type": "n8n-nodes-base.airtable",
                    "name": "Check Duplicates",
                    "parameters": {
                        "operation": "search",
                        "filterByFormula": "={{$json.searchField}}"
                    }
                }
            })

        # For missing-pagination: Add SplitInBatches
        if 'missing-pagination' in issues:
            patches.append({
                "op": "add",
                "path": "/nodes/-",
                "value": {
                    "type": "n8n-nodes-base.splitInBatches",
                    "name": "Batch Records",
                    "parameters": {
                        "batchSize": 50,
                        "options": {}
                    }
                }
            })
            patches.append({
                "op": "add",
                "path": "/nodes/-",
                "value": {
                    "type": "n8n-nodes-base.wait",
                    "name": "Rate Limit",
                    "parameters": {
                        "unit": "ms",
                        "amount": 150
                    }
                }
            })

        # For hardcoded-ids: Switch to dynamic resource locators
        if 'hardcoded-ids' in issues:
            patches.append({
                "op": "replace",
                "path": "/nodes/[airtable]/parameters/base/__rl/mode",
                "value": "list"
            })
            patches.append({
                "op": "replace",
                "path": "/nodes/[airtable]/parameters/table/__rl/mode",
                "value": "list"
            })

        # For missing-typecast: Enable typecast
        if 'missing-typecast' in issues:
            patches.append({
                "op": "add",
                "path": "/nodes/[airtable]/parameters/options",
                "value": {"typecast": True}
            })

        return patches

    def generate_tests(self, issues: Set[str]) -> List[str]:
        """Generate test cases for the remediation."""
        tests = []

        if 'blind-update' in issues:
            tests.append("Given duplicate email, Update executes and Create is skipped")
            tests.append("Given new email, Create executes and Update is skipped")

        if 'no-dedupe-before-create' in issues:
            tests.append("Given duplicate record, Create is skipped")
            tests.append("Given new record, Create executes")

        if 'missing-pagination' in issues:
            tests.append("List 500 records completes with batches and no 429 error")
            tests.append("SplitInBatches processes all items with 150ms wait between batches")

        if 'hardcoded-ids' in issues:
            tests.append("Hardcoded IDs replaced with dynamic resource locators")
            tests.append("Base and Table selection works in UI dropdowns")

        if 'missing-typecast' in issues:
            tests.append("Typecast enabled for create/update operations")
            tests.append("Number and date fields accept string inputs")

        if 'low-reliability' in issues:
            tests.append("Retry on fail enabled for all nodes")
            tests.append("Workflow recovers from transient API errors")

        return tests

    def estimate_impact(self, issues: Set[str]) -> Dict[str, str]:
        """Estimate the impact of fixes on quality scores."""
        reliability_impact = 0
        maintainability_impact = 0
        security_impact = 0

        if 'blind-update' in issues:
            reliability_impact += 15
            maintainability_impact += 5

        if 'no-dedupe-before-create' in issues:
            reliability_impact += 10

        if 'missing-pagination' in issues:
            reliability_impact += 10
            maintainability_impact += 5

        if 'hardcoded-ids' in issues:
            maintainability_impact += 15

        if 'missing-typecast' in issues:
            reliability_impact += 5

        if 'low-reliability' in issues:
            reliability_impact += 10

        if 'low-security' in issues:
            security_impact += 10

        return {
            "reliability": f"+{reliability_impact}" if reliability_impact > 0 else "+0",
            "maintainability": f"+{maintainability_impact}" if maintainability_impact > 0 else "+0",
            "security": f"+{security_impact}" if security_impact > 0 else "+0"
        }

    def generate_remediation_card(self, file_path: str, workflow_data: Dict[str, Any]) -> RemediationCard:
        """Generate a complete remediation card for a workflow."""
        issues = self.identify_issues(workflow_data)

        if not issues:
            return None

        priority = self.calculate_priority(issues)
        fix_plan = self.generate_fix_plan(issues, workflow_data)
        n8n_patches = self.generate_n8n_patches(issues, workflow_data)
        tests = self.generate_tests(issues)
        estimated_impact = self.estimate_impact(issues)

        return RemediationCard(
            filePath=file_path,
            priority=priority,
            reasons=sorted(list(issues)),
            fixPlan=fix_plan,
            n8nPatches=n8n_patches,
            tests=tests,
            estimatedImpact=estimated_impact
        )

    def generate_all_cards(self) -> List[RemediationCard]:
        """Generate remediation cards for all workflows needing fixes."""
        cards = []

        print("Analyzing workflows for remediation needs...")
        for file_path, workflow_data in self.workflows_by_path.items():
            if self.needs_remediation(workflow_data):
                card = self.generate_remediation_card(file_path, workflow_data)
                if card:
                    cards.append(card)

        print(f"Generated {len(cards)} remediation cards")

        # Sort by priority
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        cards.sort(key=lambda c: priority_order[c.priority])

        return cards

    def save_cards(self, cards: List[RemediationCard], output_path: str):
        """Save remediation cards to JSONL file."""
        print(f"Saving remediation cards to {output_path}...")

        with open(output_path, 'w') as f:
            for card in cards:
                # Convert dataclass to dict
                card_dict = {
                    'filePath': card.filePath,
                    'priority': card.priority,
                    'reasons': card.reasons,
                    'fixPlan': card.fixPlan,
                    'n8nPatches': card.n8nPatches,
                    'tests': card.tests,
                    'estimatedImpact': card.estimatedImpact
                }
                f.write(json.dumps(card_dict, separators=(',', ':')) + '\n')

        print(f"Saved {len(cards)} remediation cards")

        # Print summary
        high_count = sum(1 for c in cards if c.priority == 'high')
        medium_count = sum(1 for c in cards if c.priority == 'medium')
        low_count = sum(1 for c in cards if c.priority == 'low')

        print(f"\nPriority breakdown:")
        print(f"  High:   {high_count}")
        print(f"  Medium: {medium_count}")
        print(f"  Low:    {low_count}")


def main():
    """Main entry point."""
    descriptions_path = '/home/user/n8n-master-workflows/workflow_descriptions.jsonl'
    cards_path = '/home/user/n8n-master-workflows/workflow_cards.jsonl'
    output_path = '/home/user/n8n-master-workflows/remediation_cards.jsonl'

    planner = RemediationPlanner()
    planner.load_data(descriptions_path, cards_path)
    cards = planner.generate_all_cards()
    planner.save_cards(cards, output_path)

    print(f"\n✓ Remediation cards saved to: {output_path}")


if __name__ == '__main__':
    main()
