# src/instructions_parser.py

def parse_instructions(data):
    """Parse the instructions from JSON data.
    
    Supports multiple input formats:
    1. Standard format with "steps" array
    2. Cursor format with "actions" array
    3. Task manager format with agent routing information
    
    Args:
        data: JSON data containing instructions
        
    Returns:
        List of steps to execute
    """
    # Check for standard format with "steps" array
    if "steps" in data:
        steps = data.get("steps", [])
        # Validate each step has the required fields
        for step in steps:
            if "action" not in step:
                print(f"Warning: Step missing 'action' field: {step}")
        return steps
        
    # Check for cursor format with "actions" array
    elif "actions" in data:
        # Convert cursor actions to standard steps
        actions = data.get("actions", [])
        steps = []
        
        for action in actions:
            action_type = action.get("type")
            
            if action_type == "open_file":
                steps.append({
                    "action": "open_file",
                    "path": action.get("path")
                })
                
            elif action_type == "create_file":
                steps.append({
                    "action": "create_file",
                    "path": action.get("path"),
                    "content": action.get("content", "")
                })
                
            elif action_type == "modify_file":
                steps.append({
                    "action": "modify_file",
                    "path": action.get("path"),
                    "content": action.get("content", "")
                })
                
            elif action_type == "run_terminal":
                steps.append({
                    "action": "run_terminal",
                    "command": action.get("command")
                })
                
            elif action_type == "run_shell":
                steps.append({
                    "action": "run_command",
                    "command": action.get("command"),
                    "background": action.get("background", False)
                })
                
        return steps
        
    # Check for task manager format
    elif any(key in data for key in ["agent", "complexity", "instructions"]):
        # The task manager will handle this data directly
        return data
        
    # Fall back to returning an empty list
    print(f"Warning: Could not parse instructions from data: {data}")
    return []
