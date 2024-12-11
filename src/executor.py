# src/executor.py
import subprocess

def run_command(command, cwd=None):
    """Run a shell command and return (success, output)."""
    try:
        result = subprocess.run(command, cwd=cwd, shell=True, capture_output=True, text=True)
        success = (result.returncode == 0)
        output = result.stdout if success else result.stderr
        return success, output.strip()
    except Exception as e:
        return False, str(e)
