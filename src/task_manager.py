import json
from llm_client import ask_llm, extract_json
from prompts import TASK_MANAGER_SYSTEM_PROMPT, ROUTER_SYSTEM_PROMPT
from agents import (
    get_developer_instructions,
    get_tester_instructions,
    get_debugger_instructions,
    generate_code,
    execute_cursor_commands
)

class TaskManager:
    """Main task manager that coordinates different agents."""
    
    def __init__(self):
        """Initialize the task manager."""
        self.history = []
        
    def route_task(self, task_description):
        """Route a task to the appropriate agent based on complexity.
        
        Args:
            task_description: Description of the task
            
        Returns:
            Dictionary with routing information
        """
        response = ask_llm(ROUTER_SYSTEM_PROMPT, task_description, use_local=True)
        data = extract_json(response)
        
        if not data:
            # Default routing if extraction fails
            return {
                "route_to": "local",
                "complexity": "medium",
                "explanation": "Default routing due to parsing failure"
            }
            
        return data
        
    def execute_task(self, task_description):
        """Execute a user task by coordinating the appropriate agents.
        
        Args:
            task_description: Description of the task
            
        Returns:
            Result of the task execution
        """
        # First determine which agent should handle this and the complexity
        task_info = self.analyze_task(task_description)
        
        agent_type = task_info.get("agent", "developer")
        complexity = task_info.get("complexity", "medium")
        instructions = task_info.get("instructions", task_description)
        file_paths = task_info.get("file_paths", [])
        language = task_info.get("language", "python")
        
        # Route to the appropriate agent
        if agent_type == "developer":
            steps = get_developer_instructions(instructions, complexity)
            result = self.execute_steps(steps)
            
        elif agent_type == "code_generation":
            # For code generation, we may have multiple files to generate
            if file_paths:
                results = []
                for file_path in file_paths:
                    code = generate_code(instructions, file_path, language, complexity)
                    results.append({"file": file_path, "success": True})
                result = {"success": True, "files": results}
            else:
                code = generate_code(instructions, None, language, complexity)
                result = {"success": True, "code": code}
                
        elif agent_type == "tester":
            steps = get_tester_instructions(instructions, complexity)
            result = self.execute_steps(steps)
            
        elif agent_type == "debugger":
            steps = get_debugger_instructions(instructions, complexity)
            result = self.execute_steps(steps)
            
        elif agent_type == "cursor":
            result = execute_cursor_commands(instructions, complexity)
            
        else:
            result = {"success": False, "error": f"Unknown agent type: {agent_type}"}
            
        # Record the task and result in history
        self.history.append({
            "task": task_description,
            "analysis": task_info,
            "result": result
        })
        
        return result
        
    def analyze_task(self, task_description):
        """Analyze a task to determine how to handle it.
        
        Args:
            task_description: Description of the task
            
        Returns:
            Dictionary with task analysis
        """
        # First determine if we should use a local LLM or a more powerful one
        routing = self.route_task(task_description)
        
        # Use the appropriate LLM for task analysis based on routing
        use_local = routing.get("route_to") == "local"
        complexity = routing.get("complexity", "medium")
        
        # Get task analysis from the Task Manager agent
        response = ask_llm(
            TASK_MANAGER_SYSTEM_PROMPT,
            task_description,
            use_local=use_local,
            task_complexity=complexity
        )
        
        data = extract_json(response)
        
        if not data:
            # Default task analysis if extraction fails
            return {
                "complexity": complexity,
                "agent": "developer",
                "instructions": task_description,
                "file_paths": [],
                "language": "python"
            }
            
        # Ensure complexity from router is preserved if not specified in the task analysis
        if "complexity" not in data:
            data["complexity"] = complexity
            
        return data
    
    def execute_steps(self, steps):
        """Execute a list of steps from an agent.
        
        Args:
            steps: List of steps to execute
            
        Returns:
            Result of the execution
        """
        from main import execute_steps
        return execute_steps(steps)
        
    def get_history(self):
        """Get the task execution history.
        
        Returns:
            List of task executions
        """
        return self.history 