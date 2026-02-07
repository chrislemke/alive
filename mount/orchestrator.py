#!/usr/bin/env python3
"""
Orchestrator - Workflow automation and tool composition

Enables defining and running complex workflows that chain tools together.
"""

import subprocess
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

WORKFLOWS_FILE = Path("/home/dev/mnt/workflows.json")

class Orchestrator:
    def __init__(self):
        self.workflows = self._load_workflows()

    def _load_workflows(self) -> Dict:
        """Load workflow definitions"""
        if not WORKFLOWS_FILE.exists():
            return {
                "workflows": {
                    "knowledge_cycle": {
                        "description": "Full knowledge exploration cycle",
                        "steps": [
                            {"tool": "auto_explorer.py", "args": ["expand", "3"]},
                            {"tool": "synthesizer.py", "args": ["connections"]},
                            {"tool": "synthesizer.py", "args": ["suggest"]},
                            {"tool": "status.py", "args": []}
                        ]
                    },
                    "cross_synthesis": {
                        "description": "Deep cross-domain synthesis and analysis",
                        "steps": [
                            {"tool": "cross_synthesizer.py", "args": ["report"]},
                            {"tool": "status.py", "args": []}
                        ]
                    },
                    "daily_reflection": {
                        "description": "Reflect on progress and generate insights",
                        "steps": [
                            {"tool": "reflector.py", "args": ["insights"]},
                            {"tool": "synthesizer.py", "args": ["stats"]},
                            {"tool": "meta_optimizer.py", "args": ["report"]}
                        ]
                    },
                    "quick_status": {
                        "description": "Quick overview of all systems",
                        "steps": [
                            {"tool": "status.py", "args": []},
                            {"tool": "synthesizer.py", "args": ["stats"]}
                        ]
                    }
                }
            }

        with open(WORKFLOWS_FILE) as f:
            return json.load(f)

    def _save_workflows(self):
        """Save workflow definitions"""
        with open(WORKFLOWS_FILE, 'w') as f:
            json.dump(self.workflows, f, indent=2)

    def run_workflow(self, workflow_name: str, verbose: bool = True):
        """Execute a workflow by name"""
        if workflow_name not in self.workflows["workflows"]:
            print(f"❌ Workflow '{workflow_name}' not found")
            return False

        workflow = self.workflows["workflows"][workflow_name]

        if verbose:
            print("=" * 60)
            print(f"WORKFLOW: {workflow_name}")
            print(f"Description: {workflow['description']}")
            print("=" * 60)
            print()

        results = []
        for i, step in enumerate(workflow["steps"], 1):
            tool = step["tool"]
            args = step.get("args", [])

            if verbose:
                print(f"[{i}/{len(workflow['steps'])}] Running {tool} {' '.join(args)}")
                print("-" * 60)

            try:
                cmd = ["python3", f"/home/dev/mnt/{tool}"] + args
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=60
                )

                if result.returncode == 0:
                    if verbose:
                        print(result.stdout)
                    results.append({
                        "step": i,
                        "tool": tool,
                        "status": "success",
                        "output": result.stdout
                    })
                else:
                    if verbose:
                        print(f"❌ Error: {result.stderr}")
                    results.append({
                        "step": i,
                        "tool": tool,
                        "status": "error",
                        "error": result.stderr
                    })
                    # Continue on error by default
            except subprocess.TimeoutExpired:
                print(f"⏱ Timeout executing {tool}")
                results.append({
                    "step": i,
                    "tool": tool,
                    "status": "timeout"
                })
            except Exception as e:
                print(f"❌ Exception: {e}")
                results.append({
                    "step": i,
                    "tool": tool,
                    "status": "exception",
                    "error": str(e)
                })

            if verbose:
                print()

        if verbose:
            print("=" * 60)
            print("WORKFLOW COMPLETE")
            successful = sum(1 for r in results if r["status"] == "success")
            print(f"Results: {successful}/{len(results)} steps successful")
            print("=" * 60)

        return results

    def list_workflows(self):
        """List all available workflows"""
        print("Available Workflows:")
        print()
        for name, workflow in self.workflows["workflows"].items():
            print(f"📋 {name}")
            print(f"   {workflow['description']}")
            print(f"   Steps: {len(workflow['steps'])}")
            print()

    def add_workflow(self, name: str, description: str, steps: List[Dict]):
        """Add a new workflow"""
        self.workflows["workflows"][name] = {
            "description": description,
            "steps": steps
        }
        self._save_workflows()
        print(f"✓ Added workflow: {name}")

    def run_command_sequence(self, commands: List[str]):
        """Run a sequence of shell commands (for one-off workflows)"""
        print("Running command sequence...")
        print()

        for i, cmd in enumerate(commands, 1):
            print(f"[{i}/{len(commands)}] {cmd}")
            print("-" * 60)
            try:
                result = subprocess.run(
                    cmd,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                print(result.stdout)
                if result.returncode != 0:
                    print(f"⚠ Warning: {result.stderr}")
            except Exception as e:
                print(f"❌ Error: {e}")
            print()

def main():
    orchestrator = Orchestrator()

    if len(sys.argv) < 2:
        print("Orchestrator - Workflow Automation")
        print()
        print("Usage: orchestrator.py [command] [options]")
        print()
        print("Commands:")
        print("  list                  - List available workflows")
        print("  run <workflow_name>   - Execute a workflow")
        print("  show <workflow_name>  - Show workflow details")
        print()
        print("Examples:")
        print("  orchestrator.py list")
        print("  orchestrator.py run knowledge_cycle")
        print()
        orchestrator.list_workflows()
        sys.exit(1)

    command = sys.argv[1]

    if command == "list":
        orchestrator.list_workflows()

    elif command == "run":
        if len(sys.argv) < 3:
            print("❌ Please specify workflow name")
            sys.exit(1)

        workflow_name = sys.argv[2]
        orchestrator.run_workflow(workflow_name)

    elif command == "show":
        if len(sys.argv) < 3:
            print("❌ Please specify workflow name")
            sys.exit(1)

        workflow_name = sys.argv[2]
        if workflow_name in orchestrator.workflows["workflows"]:
            workflow = orchestrator.workflows["workflows"][workflow_name]
            print(f"Workflow: {workflow_name}")
            print(f"Description: {workflow['description']}")
            print()
            print("Steps:")
            for i, step in enumerate(workflow["steps"], 1):
                print(f"  {i}. {step['tool']} {' '.join(step.get('args', []))}")
        else:
            print(f"❌ Workflow '{workflow_name}' not found")

    else:
        print(f"❌ Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
