# Agents CLI

An AI agent system that automates coding tasks through multiple specialized agents. It seamlessly integrates with Cursor IDE and local LLMs through LLM Studio to provide a complete development workflow automation solution.

## Project Goal

The main goal of this project is to create an intelligent agent system that:

1. **Automates coding tasks** by understanding natural language instructions
2. **Leverages local LLMs** for privacy and reduced API costs using LLM Studio
3. **Intelligently routes tasks** between local and cloud LLMs based on complexity
4. **Integrates with Cursor IDE** for a seamless development experience
5. **Operates via terminal or server mode** for flexibility in different workflows

## Why Build on Top of Cursor?

Cursor already has a built-in agent that uses GPT to help you code, refactor, and answer questions about your codebase. So then:

### 🧩 **1. Granular Control and Automation**

* **Cursor's agent is reactive**: It answers when you prompt it manually.
* **Agents CLI is proactive and modular**:

  * You can *automate a sequence of tasks* (e.g., generate → test → debug → commit).
  * You can trigger agents from the **terminal, server, or scripts**, not just within the editor.

**Example**:

> `"Create a React login page"` → auto generates the file, adds tests, opens it in Cursor, and creates a commit — all through CLI.

### 💡 **2. Local LLM Support (Privacy + Cost Saving)**

* Cursor's agent uses OpenAI GPT-4 or Anthropic Claude via API.
* **Agents CLI supports local models** (via LM Studio), reducing:

  * **API cost**
  * **Latency**
  * **Data privacy concerns**

**Example**:

> `"Refactor this file"` is done via a local Mistral model, not OpenAI.

### 🔀 **3. Task Routing + Custom Agents**

* Cursor doesn't let you **define and route tasks** based on complexity.
* With Agents CLI:

  * You can **define workflows**.
  * Decide if a **simple code-gen** should go to local, and a **critical refactor** should use GPT-4.

### 🧠 **4. Memory & State Management**

* Cursor doesn't persist memory across sessions unless you handle it manually.
* Agents CLI can maintain a **long-term memory/state**, helping:

  * Track task history
  * Remember project-wide decisions
  * Reuse prior outputs

### 📡 **5. API & Server Mode = Headless DevOps**

* You can **integrate it with your own tools** (AutoMind, voice agents, web UIs).
* Run it in **server mode** and send tasks from:

  * Phone
  * Cron job
  * VSCode
  * Custom dashboard

### ✅ Feature Comparison

| Feature                       | Cursor Built-in Agent | Agents CLI System |
| ----------------------------- | --------------------- | ----------------- |
| Natural Language Coding       | ✅ Yes                 | ✅ Yes             |
| Custom Multi-Agent Workflow   | ❌ No                  | ✅ Yes             |
| Local LLM Support             | ❌ No                  | ✅ Yes             |
| Server/Terminal Automation    | ❌ No                  | ✅ Yes             |
| Memory & Task State           | ❌ Limited             | ✅ Yes             |
| Complexity-Based Task Routing | ❌ No                  | ✅ Yes             |

## Features

- **Multiple Agent Types**: Developer, Tester, Debugger, and Code Generation agents
- **Cursor IDE Integration**: Control Cursor IDE programmatically
- **Local LLM Support**: Connect to LLM Studio API for local LLM inference
- **Task Complexity Routing**: Automatically route tasks to appropriate LLMs based on complexity
- **Terminal Control**: Create and manage terminal sessions
- **Server Mode**: Run as a server to listen for tasks via API

## Installation

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your configuration (use `python setup.py` to generate a template)

## LLM Studio Integration

This project supports running inference on local models through [LM Studio](https://lmstudio.ai/). To use local models:

1. Download and install [LM Studio](https://lmstudio.ai/download)
2. Load a model in LM Studio (3B-7B parameter models recommended)
3. Start the local server from the "Local Server" tab
4. Update your `.env` file with the LM Studio configuration

### Testing LM Studio Connection

You can test your LM Studio connection using the included test utility:

```bash
python tests/lm_studio_tester.py
```

Options:
- `--model MODEL_NAME`: Specify which model to use
- `--prompt "Your test prompt"`: Test with a specific prompt
- `--check-only`: Only verify connection without sending prompts
- `--embeddings`: Test the embeddings API

## Configuration

Create a `.env` file with the following variables:

```
# API Keys for cloud-based LLMs (optional if using local LLMs only)
OPENAI_API_KEY=your_openai_api_key_here
CLAUDE_API_KEY=your_claude_api_key_here

# LM Studio Configuration (for local LLM)
LLM_STUDIO_API_URL=http://localhost:1234/v1
LLM_STUDIO_API_KEY=lm-studio
DEFAULT_LOCAL_MODEL=your-model-name-here

# Cursor IDE Configuration
CURSOR_API_URL=http://localhost:8765

# Task Agent Configuration
DEFAULT_COMPLEXITY=medium  # low, medium, high
DEFAULT_LANGUAGE=python

# Use mock responses for testing without API keys
USE_MOCK_RESPONSES=false
```

## Usage

### Run a Project Workflow

```
python src/main.py project --dir my_project
```

### Execute Developer Agent

```
python src/main.py dev "Create a simple Flask API with user authentication"
```

### Execute a General Task

```
python src/main.py task "Create a React component for a login form"
```

### Generate Code

```
python src/main.py code "Create a function to parse CSV files" --file parser.py --language python
```

### Execute Cursor IDE Commands

```
python src/main.py cursor "Open the file main.py and add a new function to handle authentication"
```

### Run in Server Mode

```
python src/main.py server --port 8080
```

You can then send tasks to the server via HTTP:

```
curl -X POST http://localhost:8080/execute -H "Content-Type: application/json" -d '{"task": "Create a function to validate email addresses"}'
```

## Architecture

The system is composed of several modules:

- `main.py`: CLI interface and entry point
- `task_manager.py`: Coordinates tasks between agents and routes to appropriate LLM
- `agents.py`: Manages different specialized agent types
- `llm_client.py`: Unified interface to OpenAI, Claude, and LM Studio APIs
- `cursor_integration.py`: Handles Cursor IDE integration
- `file_manager.py`: Handles file operations
- `env_manager.py`: Manages virtual environments
- `executor.py`: Executes shell commands
- `state_manager.py`: Manages application state
- `prompts.py`: Contains system prompts for different agents
- `instructions_parser.py`: Parses instructions from LLM responses

## Agent Types

- **Developer Agent**: Creates project structures, files, and runs commands
- **Tester Agent**: Tests code and fixes issues
- **Debugger Agent**: Analyzes and fixes errors
- **Code Generation Agent**: Generates code based on descriptions

## Task Complexity Routing

Tasks are automatically routed based on complexity:

- **Low**: Simple tasks handled by local LLM through LM Studio
- **Medium**: Moderate tasks that may use OpenAI or local LLM
- **High**: Complex coding tasks that require Claude or GPT-4

## Testing

For testing without actual API access, set `USE_MOCK_RESPONSES=true` in your `.env` file.
