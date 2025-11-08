#!/usr/bin/env python3
import json
import sys
from pathlib import Path
from collections import defaultdict

def extract_workflow_info(filepath):
    """Extract key information from a workflow JSON file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            workflow = json.load(f)

        # Extract workflow name
        name = workflow.get('name', Path(filepath).stem)

        # Extract nodes to find integrations and triggers
        nodes = workflow.get('nodes', [])

        # Find trigger nodes
        triggers = []
        integrations = set()
        node_types = []

        for node in nodes:
            node_type = node.get('type', '')
            node_name = node.get('name', '')

            # Skip sticky notes
            if 'stickyNote' in node_type:
                continue

            node_types.append(node_type)

            # Identify triggers
            if 'trigger' in node_type.lower() or 'trigger' in node_name.lower():
                triggers.append({
                    'type': node_type,
                    'name': node_name
                })

            # Extract integration names from node types
            if 'n8n-nodes-base.' in node_type:
                integration = node_type.replace('n8n-nodes-base.', '')
                # Clean up common node types
                if integration not in ['noOp', 'set', 'code', 'if', 'merge', 'splitInBatches',
                                       'wait', 'httpRequest', 'function', 'filter', 'switch',
                                       'executeWorkflow', 'stickyNote']:
                    integrations.add(integration)
            elif '@n8n/n8n-nodes-langchain' in node_type:
                integration = 'LangChain/' + node_type.split('.')[-1]
                integrations.add(integration)

            # Add specific service names
            if node_type in ['@n8n/n8n-nodes-langchain.openAi',
                           '@n8n/n8n-nodes-langchain.lmChatOpenAi']:
                integrations.add('OpenAI')

        # Determine primary trigger type
        trigger_type = 'Manual'
        if triggers:
            trigger_node = triggers[0]['type']
            if 'schedule' in trigger_node.lower():
                trigger_type = 'Schedule'
            elif 'webhook' in trigger_node.lower():
                trigger_type = 'Webhook'
            elif 'chat' in trigger_node.lower():
                trigger_type = 'Chat'
            elif 'telegram' in trigger_node.lower():
                trigger_type = 'Telegram'
            elif 'email' in trigger_node.lower():
                trigger_type = 'Email'
            else:
                trigger_type = triggers[0]['name'] if triggers[0]['name'] else trigger_node

        # Extract description from sticky notes if available
        description = ''
        for node in nodes:
            if node.get('type') == 'n8n-nodes-base.stickyNote':
                content = node.get('parameters', {}).get('content', '')
                if content and len(content) > len(description):
                    description = content

        if not description:
            description = f"Workflow: {name}"

        # Clean up description - take first meaningful line
        if description:
            lines = [line.strip() for line in description.split('\n') if line.strip() and not line.strip().startswith('#')]
            description = lines[0] if lines else description[:200]

        return {
            'name': name,
            'description': description[:300],  # Limit description length
            'integrations': sorted(list(integrations)),
            'trigger_type': trigger_type,
            'node_count': len([n for n in nodes if 'stickyNote' not in n.get('type', '')])
        }

    except Exception as e:
        return {
            'name': Path(filepath).stem,
            'description': f'Error parsing: {str(e)}',
            'integrations': [],
            'trigger_type': 'Unknown',
            'node_count': 0
        }

def analyze_directory(files):
    """Analyze a list of workflow files."""
    results = []
    for filepath in files:
        info = extract_workflow_info(filepath)
        results.append(info)
    return results

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: analyze_workflows.py <file1> <file2> ...")
        sys.exit(1)

    files = sys.argv[1:]
    results = analyze_directory(files)

    # Output as JSON
    print(json.dumps(results, indent=2))
