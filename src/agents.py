# src/agents.py
from llm_client import ask_llm, extract_json
from instructions_parser import parse_instructions
from prompts import (
    DEVELOPER_SYSTEM_PROMPT, 
    DEVELOPER_USER_PROMPT, 
    TESTER_SYSTEM_PROMPT, 
    TESTER_USER_PROMPT, 
    DEBUGGER_SYSTEM_PROMPT,
    CODE_GENERATION_SYSTEM_PROMPT,
    CURSOR_INTEGRATION_SYSTEM_PROMPT
)
from cursor_integration import CursorIntegration

# Initialize cursor integration
cursor = CursorIntegration()

def get_developer_instructions(custom_prompt=None, complexity="medium"):
    """Get instructions from the developer agent.
    
    Args:
        custom_prompt: Custom user prompt (if None, use default)
        complexity: Task complexity level
        
    Returns:
        List of parsed instructions
    """
    user_prompt = custom_prompt or DEVELOPER_USER_PROMPT
    response = ask_llm(DEVELOPER_SYSTEM_PROMPT, user_prompt, task_complexity=complexity)
    data = extract_json(response)
    if data:
        return parse_instructions(data)
    return []

def get_tester_instructions(custom_prompt=None, complexity="low"):
    """Get instructions from the tester agent.
    
    Args:
        custom_prompt: Custom user prompt (if None, use default)
        complexity: Task complexity level
        
    Returns:
        List of parsed instructions
    """
    user_prompt = custom_prompt or TESTER_USER_PROMPT
    response = ask_llm(TESTER_SYSTEM_PROMPT, user_prompt, task_complexity=complexity)
    data = extract_json(response)
    if data:
        return parse_instructions(data)
    return []

def get_debugger_instructions(error_msg, complexity="medium"):
    """Get instructions from the debugger agent.
    
    Args:
        error_msg: Error message to debug
        complexity: Task complexity level
        
    Returns:
        List of parsed instructions
    """
    response = ask_llm(
        DEBUGGER_SYSTEM_PROMPT, 
        f"Error encountered:\n{error_msg}\nFix the code. Return JSON steps only.",
        task_complexity=complexity
    )
    data = extract_json(response)
    if data:
        return parse_instructions(data)
    return []

def generate_code(description, file_path=None, language="python", complexity="high"):
    """Generate code based on description.
    
    Args:
        description: Description of the code to generate
        file_path: Path to the file where the code will be saved
        language: Programming language
        complexity: Task complexity level
        
    Returns:
        Generated code
    """
    system_prompt = CODE_GENERATION_SYSTEM_PROMPT.format(language=language)
    user_prompt = f"Generate code for: {description}"
    
    if file_path:
        user_prompt += f"\nThe code will be saved to {file_path}."
        
    response = ask_llm(system_prompt, user_prompt, task_complexity=complexity)
    
    # Extract code from markdown code blocks if present
    import re
    code_pattern = r"```(?:\w+)?\n(.*?)\n```"
    matches = re.findall(code_pattern, response, re.DOTALL)
    
    if matches:
        code = matches[0]
    else:
        code = response
        
    if file_path:
        cursor.create_file_direct(file_path, code)
        
    return code

def execute_cursor_commands(instructions, complexity="medium"):
    """Execute instructions in Cursor IDE.
    
    Args:
        instructions: User instructions for Cursor operations
        complexity: Task complexity level
        
    Returns:
        Response from execution
    """
    # Create a terminal if we don't have one already
    terminal_id = cursor.create_terminal()
    
    response = ask_llm(
        CURSOR_INTEGRATION_SYSTEM_PROMPT, 
        instructions,
        task_complexity=complexity
    )
    
    data = extract_json(response)
    if not data or "actions" not in data:
        return {"success": False, "message": "Could not parse instructions"}
        
    actions = data["actions"]
    results = []
    
    for action in actions:
        action_type = action.get("type")
        
        if action_type == "open_file":
            file_path = action.get("path")
            success = cursor.open_file(file_path)
            results.append({"type": "open_file", "path": file_path, "success": success})
            
        elif action_type == "create_file":
            file_path = action.get("path")
            content = action.get("content", "")
            success = cursor.create_file_direct(file_path, content)
            results.append({"type": "create_file", "path": file_path, "success": success})
            
        elif action_type == "modify_file":
            file_path = action.get("path")
            content = action.get("content")
            success = cursor.modify_file(file_path, content)
            results.append({"type": "modify_file", "path": file_path, "success": success})
            
        elif action_type == "run_terminal":
            command = action.get("command")
            if terminal_id:
                success = cursor.run_in_terminal(terminal_id, command)
                results.append({"type": "run_terminal", "command": command, "success": success})
            else:
                # Fall back to running directly
                result = cursor.run_shell_command_in_os(command)
                results.append({"type": "run_shell", "command": command, "result": result})
                
        elif action_type == "run_shell":
            command = action.get("command")
            background = action.get("background", False)
            result = cursor.run_shell_command_in_os(command, capture_output=not background)
            results.append({"type": "run_shell", "command": command, "result": result})
    
    return {"success": True, "results": results}
