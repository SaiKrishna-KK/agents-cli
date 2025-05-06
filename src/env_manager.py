# src/env_manager.py
import os
from executor import run_command

def create_venv(venv_path):
    cmd = f"python -m venv {venv_path}"
    return run_command(cmd)

def install_dependencies(dependencies, venv_path):
    python_executable = get_python_executable(venv_path)
    for dep in dependencies:
        success, output = run_command(f"{python_executable} -m pip install {dep}")
        if not success:
            return False, output
    return True, "Dependencies installed successfully."

def run_python_file(file_path, venv_path):
    python_executable = get_python_executable(venv_path)
    return run_command(f"\"{python_executable}\" \"{file_path}\"")

def run_shell_command(command, venv_path, background=False):
    env = os.environ.copy()
    scripts_path = os.path.join(venv_path, 'Scripts' if os.name == 'nt' else 'bin')
    env["PATH"] = scripts_path + os.pathsep + env["PATH"]
    # For simplicity, just run in current directory; background handled in run_command directly
    return run_command(command, cwd=os.getcwd(), background=background)

def get_python_executable(venv_path):
    if os.name == 'nt':
        return os.path.join(venv_path, 'Scripts', 'python.exe')
    else:
        return os.path.join(venv_path, 'bin', 'python')
