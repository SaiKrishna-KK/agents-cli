# src/file_manager.py
from pathlib import Path

def create_file(file_path, content):
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
