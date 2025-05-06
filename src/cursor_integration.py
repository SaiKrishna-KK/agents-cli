import os
import json
import requests
import subprocess
from pathlib import Path
from urllib.parse import urljoin

class CursorIntegration:
    """Integration with Cursor IDE for managing files, terminals, and IDE features."""
    
    def __init__(self, api_url=None, workspace_path=None):
        """Initialize the cursor integration.
        
        Args:
            api_url: URL for Cursor's API
            workspace_path: Path to the current workspace
        """
        self.api_url = api_url or os.getenv("CURSOR_API_URL", "http://localhost:8765")
        self.workspace_path = workspace_path or os.getcwd()
        self.use_mock = os.getenv("USE_MOCK_RESPONSES", "false").lower() == "true"
        self.mock_terminal_id = "mock-terminal-1"
        
    def _make_api_request(self, endpoint, method="GET", data=None):
        """Make a request to the Cursor API.
        
        Args:
            endpoint: API endpoint
            method: HTTP method
            data: Request payload
            
        Returns:
            Response from the API
        """
        # For testing, use mock responses
        if self.use_mock:
            if endpoint == "terminal/create":
                return {"id": self.mock_terminal_id, "name": data.get("name", "Agent Terminal")}
            elif endpoint.startswith("terminal/") and "/execute" in endpoint:
                return {"success": True}
            elif endpoint == "active-file":
                return {"path": os.path.join(self.workspace_path, "mock_active_file.py")}
            elif endpoint == "open":
                return {"success": True}
            elif endpoint == "modify":
                return {"success": True}
            else:
                return {"success": True}
        
        # Real API request
        url = urljoin(self.api_url, endpoint)
        try:
            if method == "GET":
                response = requests.get(url)
            elif method == "POST":
                response = requests.post(url, json=data)
            elif method == "PUT":
                response = requests.put(url, json=data)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
                
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error communicating with Cursor API: {str(e)}")
            return None
            
    def open_file(self, file_path):
        """Open a file in Cursor.
        
        Args:
            file_path: Path to the file to open
            
        Returns:
            True if successful, False otherwise
        """
        # If using mock, just check if file exists
        if self.use_mock:
            if not os.path.isabs(file_path):
                file_path = os.path.join(self.workspace_path, file_path)
            return os.path.exists(file_path)
        
        # Regular implementation
        # If file_path is relative, make it absolute
        if not os.path.isabs(file_path):
            file_path = os.path.join(self.workspace_path, file_path)
            
        return self._make_api_request("open", method="POST", data={"path": file_path}) is not None
        
    def create_terminal(self, name="Agent Terminal"):
        """Create a new terminal in Cursor.
        
        Args:
            name: Name for the terminal
            
        Returns:
            Terminal ID if successful, None otherwise
        """
        response = self._make_api_request("terminal/create", method="POST", data={"name": name})
        if response and "id" in response:
            return response["id"]
        return None
        
    def run_in_terminal(self, terminal_id, command):
        """Run a command in a specific terminal.
        
        Args:
            terminal_id: ID of the terminal
            command: Command to run
            
        Returns:
            True if successful, False otherwise
        """
        # If using mock, run the command directly
        if self.use_mock:
            result = self.run_shell_command_in_os(command)
            return result.get("success", False)
        
        return self._make_api_request(
            f"terminal/{terminal_id}/execute", 
            method="POST", 
            data={"command": command}
        ) is not None
        
    def get_active_file(self):
        """Get the currently active file in Cursor.
        
        Returns:
            Path to the active file if successful, None otherwise
        """
        response = self._make_api_request("active-file")
        if response and "path" in response:
            return response["path"]
        return None
        
    def modify_file(self, file_path, content):
        """Modify a file in Cursor.
        
        Args:
            file_path: Path to the file to modify
            content: New content for the file
            
        Returns:
            True if successful, False otherwise
        """
        # If using mock, write to the file directly
        if self.use_mock:
            return self.create_file_direct(file_path, content)
        
        # Regular implementation
        # If file_path is relative, make it absolute
        if not os.path.isabs(file_path):
            file_path = os.path.join(self.workspace_path, file_path)
            
        return self._make_api_request(
            "modify", 
            method="POST", 
            data={"path": file_path, "content": content}
        ) is not None
        
    def run_shell_command_in_os(self, command, cwd=None, capture_output=True):
        """Run a shell command directly in the OS.
        
        Args:
            command: Command to run
            cwd: Current working directory
            capture_output: Whether to capture the output
            
        Returns:
            Command output if capture_output is True, else None
        """
        try:
            if capture_output:
                result = subprocess.run(
                    command, 
                    shell=True, 
                    cwd=cwd or self.workspace_path,
                    text=True,
                    capture_output=True
                )
                return {
                    "success": result.returncode == 0,
                    "stdout": result.stdout,
                    "stderr": result.stderr
                }
            else:
                # Just run the command without capturing output
                subprocess.Popen(
                    command,
                    shell=True,
                    cwd=cwd or self.workspace_path
                )
                return {"success": True}
        except Exception as e:
            print(f"Error running shell command: {str(e)}")
            return {"success": False, "error": str(e)}
            
    def create_file_direct(self, file_path, content=""):
        """Create a file directly in the filesystem.
        
        Args:
            file_path: Path to the file to create
            content: Content to write to the file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # If file_path is relative, make it absolute
            if not os.path.isabs(file_path):
                file_path = os.path.join(self.workspace_path, file_path)
                
            # Ensure the directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Write the file
            with open(file_path, "w") as f:
                f.write(content)
                
            return True
        except Exception as e:
            print(f"Error creating file: {str(e)}")
            return False
            
    def open_cursor_ide(self, workspace_path=None):
        """Open the Cursor IDE with a specific workspace.
        
        Args:
            workspace_path: Path to the workspace to open
            
        Returns:
            True if successful, False otherwise
        """
        # If using mock, just return success
        if self.use_mock:
            print("Mock: Opening Cursor IDE...")
            return True
            
        workspace_path = workspace_path or self.workspace_path
        
        try:
            # Check for different OS platforms
            if os.name == 'nt':  # Windows
                cursor_path = os.path.expandvars("%LOCALAPPDATA%\\Programs\\Cursor\\Cursor.exe")
                if not os.path.exists(cursor_path):
                    cursor_path = os.path.expandvars("%USERPROFILE%\\AppData\\Local\\Programs\\Cursor\\Cursor.exe")
            elif os.name == 'posix':  # macOS or Linux
                if os.path.exists("/Applications/Cursor.app"):
                    cursor_path = "/Applications/Cursor.app"
                else:
                    cursor_path = None
            else:
                cursor_path = None
                
            if cursor_path:
                if os.name == 'nt':  # Windows
                    subprocess.Popen([cursor_path, workspace_path])
                elif os.name == 'posix':  # macOS
                    subprocess.Popen(["open", "-a", cursor_path, workspace_path])
                return True
            else:
                print("Could not locate Cursor application")
                return False
        except Exception as e:
            print(f"Error opening Cursor: {str(e)}")
            return False 