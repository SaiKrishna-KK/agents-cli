# src/main.py
import os
import sys
import argparse
import json
from dotenv import load_dotenv
from task_manager import TaskManager
from agents import (
    get_developer_instructions, 
    get_tester_instructions, 
    get_debugger_instructions,
    execute_cursor_commands
)
from file_manager import (
    create_file, 
    modify_file, 
    file_exists, 
    read_file, 
    create_directory,
    delete_file
)
from env_manager import (
    create_venv, 
    install_dependencies, 
    run_python_file, 
    run_shell_command
)
from state_manager import (
    record_action, 
    record_file, 
    load_state, 
    save_state
)
from executor import kill_all_background_processes
from cursor_integration import CursorIntegration

# Load environment variables from .env file
load_dotenv()

# Initialize task manager
task_manager = TaskManager()

# Initialize cursor integration
cursor = CursorIntegration()

def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(description="Agent-based CLI tool")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Project command
    project_parser = subparsers.add_parser("project", help="Run a project-building workflow")
    project_parser.add_argument("--dir", default="llm-cli-testing", help="Project directory")
    
    # Dev command
    dev_parser = subparsers.add_parser("dev", help="Execute developer agent")
    dev_parser.add_argument("instructions", help="Developer instructions")
    
    # Task command
    task_parser = subparsers.add_parser("task", help="Execute a general task")
    task_parser.add_argument("instructions", help="Task instructions")
    
    # Code command
    code_parser = subparsers.add_parser("code", help="Generate code")
    code_parser.add_argument("description", help="Code description")
    code_parser.add_argument("--file", help="Output file path")
    code_parser.add_argument("--language", default="python", help="Programming language")
    
    # Cursor command
    cursor_parser = subparsers.add_parser("cursor", help="Execute cursor commands")
    cursor_parser.add_argument("instructions", help="Cursor instructions")
    
    # Server command
    server_parser = subparsers.add_parser("server", help="Run a server to listen for commands")
    server_parser.add_argument("--port", type=int, default=8080, help="Server port")
    
    # Parse arguments
    args = parser.parse_args()
    
    if args.command == "project":
        run_project_workflow(args.dir)
    elif args.command == "dev":
        run_developer_agent(args.instructions)
    elif args.command == "task":
        run_task(args.instructions)
    elif args.command == "code":
        generate_code(args.description, args.file, args.language)
    elif args.command == "cursor":
        run_cursor_commands(args.instructions)
    elif args.command == "server":
        run_server(args.port)
    else:
        parser.print_help()

def run_project_workflow(project_dir):
    """Run a complete project-building workflow.
    
    Args:
        project_dir: Project directory
    """
    # Ensure project directory
    os.makedirs(project_dir, exist_ok=True)
    os.chdir(project_dir)

    # Phase 1: Developer instructions (create app, run server in background, etc.)
    dev_steps = get_developer_instructions()
    if not dev_steps:
        print("No valid instructions from Developer.")
        return

    execute_steps(dev_steps)

    # Phase 2: Tester instructions
    print("=== TESTING PHASE ===")
    test_steps = get_tester_instructions()
    if test_steps:
        execute_steps(test_steps)

    # After tests, if we want, we can kill all background processes
    kill_all_background_processes()

    print("Project workflow completed successfully.")

def run_developer_agent(instructions):
    """Run the developer agent with custom instructions.
    
    Args:
        instructions: Custom instructions for the developer agent
    """
    steps = get_developer_instructions(instructions)
    if not steps:
        print("No valid instructions from Developer.")
        return
        
    execute_steps(steps)
    print("Developer agent completed successfully.")

def run_task(instructions):
    """Run a general task using the task manager.
    
    Args:
        instructions: Task instructions
    """
    print(f"Executing task: {instructions}")
    result = task_manager.execute_task(instructions)
    
    if result.get("success", False):
        print("Task completed successfully.")
    else:
        print(f"Task failed: {result.get('error', 'Unknown error')}")
        
    return result

def generate_code(description, file_path=None, language="python"):
    """Generate code based on a description.
    
    Args:
        description: Code description
        file_path: Optional file path to save the generated code
        language: Programming language
    """
    from agents import generate_code as gen_code
    
    print(f"Generating {language} code for: {description}")
    code = gen_code(description, file_path, language)
    
    if file_path:
        print(f"Code saved to {file_path}")
    else:
        print("Generated code:")
        print(code)
        
    return code

def run_cursor_commands(instructions):
    """Run commands in Cursor IDE.
    
    Args:
        instructions: Instructions for cursor operations
    """
    print(f"Executing cursor commands: {instructions}")
    result = execute_cursor_commands(instructions)
    
    if result.get("success", False):
        print("Cursor commands executed successfully.")
        for res in result.get("results", []):
            print(f"- {res.get('type')}: {'Success' if res.get('success', False) else 'Failed'}")
    else:
        print(f"Failed to execute cursor commands: {result.get('message', 'Unknown error')}")
        
    return result

def run_server(port):
    """Run a server to listen for commands.
    
    Args:
        port: Server port
    """
    try:
        from flask import Flask, request, jsonify
        
        app = Flask(__name__)
        
        @app.route('/execute', methods=['POST'])
        def execute():
            """Execute a task from the request."""
            data = request.json
            if not data or 'task' not in data:
                return jsonify({"error": "Missing task parameter"}), 400
                
            task = data['task']
            result = task_manager.execute_task(task)
            return jsonify(result)
            
        @app.route('/status', methods=['GET'])
        def status():
            """Get the agent status."""
            history = task_manager.get_history()
            return jsonify({
                "status": "running",
                "tasks_completed": len(history)
            })
            
        print(f"Starting server on port {port}...")
        app.run(host='0.0.0.0', port=port)
    except ImportError:
        print("Flask is required to run the server. Install it with: pip install flask")
        return

def execute_steps(steps):
    """Execute a list of steps from an agent.
    
    Args:
        steps: List of steps to execute
        
    Returns:
        Dictionary with execution results
    """
    results = []
    
    for i, step in enumerate(steps):
        action = step.get("action")
        result = {"step": i, "action": action, "success": False}
        
        try:
            if action == "create_venv":
                venv_path = step.get("path", "./venv")
                abs_venv = os.path.abspath(venv_path)
                success, output = create_venv(abs_venv)
                print("Create venv:", output)
                result["success"] = success
                result["output"] = output
                
                if not success:
                    handle_failure(output)
                    break

            elif action == "install_deps":
                deps = step.get("deps", [])
                venv_path = step.get("venv", "./venv")
                abs_venv = os.path.abspath(venv_path)
                success, output = install_dependencies(deps, abs_venv)
                print("Install deps:", output)
                result["success"] = success
                result["output"] = output
                
                if not success:
                    handle_failure(output)
                    break

            elif action == "create_file":
                file_path = step.get("path")
                content = step.get("content", "")
                success = create_file(file_path, content)
                print(f"Created file {file_path}")
                record_file(file_path)
                result["success"] = success
                result["output"] = f"File {file_path} created."

            elif action == "modify_file":
                file_path = step.get("path")
                content = step.get("content", "")
                success = modify_file(file_path, content)
                print(f"Modified file {file_path}")
                result["success"] = success
                result["output"] = f"File {file_path} modified."

            elif action == "run_file":
                file_path = step.get("file")
                venv_path = step.get("venv", "./venv")
                success, output = run_python_file(file_path, os.path.abspath(venv_path))
                print(f"Run file {file_path}:", output)
                result["success"] = success
                result["output"] = output
                
                if not success:
                    retry_with_debugger(output)
                    break

            elif action == "run_command":
                command = step.get("command")
                venv_path = step.get("venv", "./venv")
                background = step.get("background", False)
                success, output = run_shell_command(command, os.path.abspath(venv_path), background=background)
                print(f"Run command {command}:", output)
                result["success"] = success
                result["output"] = output
                
                if not success:
                    retry_with_debugger(output)
                    break

            elif action == "kill_process":
                # Kill all background processes
                kill_all_background_processes()
                result["success"] = True
                result["output"] = "Killed all background processes."
                
            elif action == "open_file":
                file_path = step.get("path")
                success = cursor.open_file(file_path)
                print(f"Opened file {file_path}")
                result["success"] = success
                result["output"] = f"File {file_path} opened."
                
            elif action == "run_terminal":
                command = step.get("command")
                # Create a terminal if needed
                terminal_id = cursor.create_terminal()
                if terminal_id:
                    success = cursor.run_in_terminal(terminal_id, command)
                    result["success"] = success
                    result["output"] = f"Command '{command}' run in terminal."
                else:
                    # Fall back to running directly
                    cmd_result = cursor.run_shell_command_in_os(command)
                    result["success"] = cmd_result.get("success", False)
                    result["output"] = cmd_result.get("stdout", "")
                
            else:
                print(f"Unknown action: {action}")
                result["success"] = False
                result["output"] = f"Unknown action: {action}"
                
        except Exception as e:
            print(f"Error executing step {i} ({action}): {str(e)}")
            result["success"] = False
            result["output"] = f"Error: {str(e)}"
            
        # Record the action
        record_action(result)
        results.append(result)
        
        # Stop if a step failed
        if not result["success"]:
            break
            
    return {"success": all(r["success"] for r in results), "results": results}

def handle_failure(error_msg):
    """Handle a failure by printing the error message.
    
    Args:
        error_msg: Error message
    """
    print("Failure encountered:", error_msg)
    retry_with_debugger(error_msg)

def retry_with_debugger(error_msg):
    """Retry execution with the debugger agent.
    
    Args:
        error_msg: Error message
    """
    new_steps = get_debugger_instructions(error_msg)
    if new_steps:
        execute_steps(new_steps)
    else:
        print("No revised instructions from debugger. Stopping.")


if __name__ == "__main__":
    main()
