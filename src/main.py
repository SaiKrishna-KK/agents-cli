
# src/main.py
import os
import sys
from .llm_client import ask_llm
from .prompts import SYSTEM_PROMPT, USER_PROMPT
from .instructions_parser import parse_instructions
from .env_manager import create_venv, install_dependencies, run_python_file
from .file_manager import create_file

def main():
    # Ensure the llm-cli-testing directory exists
    project_dir = "llm-cli-testing"
    os.makedirs(project_dir, exist_ok=True)
    os.chdir(project_dir)

    instructions = ask_llm(SYSTEM_PROMPT, USER_PROMPT)
    steps = parse_instructions(instructions)

    if not steps:
        print("No valid instructions returned by LLM.")
        sys.exit(1)

    venv_path = None
    execution_log = []

    for i, step in enumerate(steps):
        action = step.get("action")
        if action == "create_venv":
            venv_path = step.get("path", "./venv")
            # Make venv_path absolute based on the project_dir
            venv_path = os.path.abspath(venv_path)
            success, output = create_venv(venv_path)
            execution_log.append({"step": i, "action": action, "success": success, "output": output})
            print("Create venv:", output)
            if not success:
                print("Checking if python in venv exists:", os.path.exists(os.path.join(venv_path, 'Scripts', 'python.exe')))
                break

        elif action == "install_deps":
            deps = step.get("deps", [])
            success, output = install_dependencies(deps, venv_path=venv_path)
            execution_log.append({"step": i, "action": action, "success": success, "output": output})
            print("Install deps:", output)
            if not success:
                break

        elif action == "create_file":
            file_path = step.get("path")
            content = step.get("content", "")
            create_file(file_path, content)
            execution_log.append({"step": i, "action": action, "success": True, "output": f"File {file_path} created."})
            print(f"Created file {file_path}")

        elif action == "run_file":
            file_path = step.get("file")
            success, output = run_python_file(file_path, venv_path=venv_path)
            execution_log.append({"step": i, "action": action, "success": success, "output": output})
            print(f"Run file {file_path}:", output)
            if not success:
                # If code execution failed, send error back to LLM and get revised instructions
                error_feedback = f"The code failed with error:\n{output}"
                revised_instructions = ask_llm(SYSTEM_PROMPT, error_feedback)
                print("LLM Revised Instructions:\n", revised_instructions)
                # In a real scenario, parse and retry. Here, just stop.
                break

    # Print final execution log
    print("Execution log:")
    for entry in execution_log:
        print(entry)

if __name__ == "__main__":
    main()

