# src/instructions_parser.py


import json
import re

def parse_instructions(json_str):
    # Attempt to find a JSON object in the string:
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

    match = re.search(r'\{.*\}', json_str, flags=re.DOTALL)
    if match:
        pure_json = match.group(0)
        try:
            data = json.loads(pure_json)
            steps = data.get("steps", [])
            return steps
        except json.JSONDecodeError:
            return []
    else:
        return []
