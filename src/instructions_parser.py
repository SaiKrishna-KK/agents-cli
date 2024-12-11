# src/instructions_parser.py
import json

def parse_instructions(json_str):
    """
    Parse the LLM's JSON instructions.
    Expected format:
    {
      "steps": [
        {"action": "create_venv", "path": "./venv"},
        {"action": "install_deps", "deps": ["requests"]},
        {"action": "create_file", "path": "main.py", "content": "print('Hello, World!')"},
        {"action": "run_file", "file": "main.py", "venv": "./venv"}
      ]
    }
    """
    try:
        data = json.loads(json_str)
        steps = data.get("steps", [])
        return steps
    except json.JSONDecodeError:
        # If instructions aren't valid JSON, return empty list
        return []
