# src/env_manager.py
import os
from .executor import run_command

def create_venv(venv_path):
    command = f"python -m venv {venv_path}"
    return run_command(command)

def install_dependencies(dependencies, venv_path=None):
    if venv_path:
        python_executable = os.path.join(venv_path, 'Scripts', 'python.exe') if os.name == 'nt' else os.path.join(venv_path, 'bin', 'python')
    else:
        python_executable = 'python'
    for dep in dependencies:
        success, output = run_command(f"{python_executable} -m pip install {dep}")
        if not success:
            return False, output
    return True, "Dependencies installed successfully."

def run_python_file(file_path, venv_path=None):
    if venv_path:
        python_executable = os.path.join(venv_path, 'Scripts', 'python.exe') if os.name == 'nt' else os.path.join(venv_path, 'bin', 'python')
    else:
        python_executable = 'python'
    success, output = run_command(f"{python_executable} {file_path}")
    return success, output
