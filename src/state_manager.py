# src/state_manager.py
import json
import os

STATE_FILE = "state.json"

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"files": [], "actions": [], "background_processes": []}

def save_state(state):
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2)

def record_action(action_detail):
    state = load_state()
    state["actions"].append(action_detail)
    save_state(state)

def record_file(file_path):
    state = load_state()
    if file_path not in state["files"]:
        state["files"].append(file_path)
    save_state(state)
