import os
import shutil
import sys
from pathlib import Path

def create_env_sample():
    """Create the sample .env file"""
    sample = """# API Keys
OPENAI_API_KEY=your_openai_api_key_here
CLAUDE_API_KEY=your_claude_api_key_here

# LLM Studio Configuration (for local LLM)
LLM_STUDIO_API_URL=http://localhost:8000/v1/chat/completions
LLM_STUDIO_API_KEY=
DEFAULT_LOCAL_MODEL=default

# Cursor IDE Configuration
CURSOR_API_URL=http://localhost:8765

# Task Agent Configuration
DEFAULT_COMPLEXITY=medium  # low, medium, high
DEFAULT_LANGUAGE=python
"""
    # Write to both locations for convenience
    with open(".env.sample", "w") as f:
        f.write(sample)
    
    os.makedirs("src", exist_ok=True)
    with open("src/.env.sample", "w") as f:
        f.write(sample)
    
    print("Created .env.sample files")

def create_env_file():
    """Create the .env file from the sample if it doesn't exist"""
    if not os.path.exists(".env"):
        if os.path.exists(".env.sample"):
            shutil.copy(".env.sample", ".env")
            print("Created .env file from sample")
        else:
            create_env_sample()
            shutil.copy(".env.sample", ".env")
            print("Created .env file")
    else:
        print(".env file already exists")

def setup_environment():
    """Set up the environment for the agent CLI"""
    # Create .env file
    create_env_sample()
    create_env_file()
    
    # Create directories
    os.makedirs("src", exist_ok=True)
    
    print("\nSetup complete!")
    print("\nNext steps:")
    print("1. Edit the .env file with your API keys")
    print("2. Install dependencies with: pip install -r requirements.txt")
    print("3. Run the CLI with: python src/main.py --help")

if __name__ == "__main__":
    setup_environment() 