# src/executor.py
import subprocess
import os
from state_manager import record_action, load_state, save_state

def run_command(command, cwd=None, background=False):
    print(f"Running command: {command}, background={background}")
    if background:
        # Run the process in background and return immediately
        process = subprocess.Popen(command, cwd=cwd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        # Store PID in state
        state = load_state()
        if "background_processes" not in state:
            state["background_processes"] = []
        state["background_processes"].append({"command": command, "pid": process.pid})
        save_state(state)
        return True, f"Started background process PID: {process.pid}"
    else:
        result = subprocess.run(command, cwd=cwd, shell=True, capture_output=True, text=True)
        success = (result.returncode == 0)
        output = result.stdout if success else result.stderr
        return success, output.strip()

def kill_all_background_processes():
    state = load_state()
    if "background_processes" in state:
        for proc_info in state["background_processes"]:
            pid = proc_info["pid"]
            try:
                if os.name == 'nt':
                    subprocess.run(f"taskkill /PID {pid} /F")
                else:
                    os.kill(pid, 9)
                print(f"Killed process PID: {pid}")
            except Exception as e:
                print(f"Error killing PID {pid}: {e}")
        # Clear the list
        state["background_processes"] = []
        save_state(state)
