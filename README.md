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

## Detailed Usage Guide

This section provides a comprehensive explanation of how to use the Agents CLI effectively for different workflows and scenarios.

### Command Structure

All commands follow this general format:
```
python src/main.py COMMAND [OPTIONS] "INSTRUCTIONS"
```

Where:
- `COMMAND` is one of: project, dev, task, code, cursor, server
- `OPTIONS` are command-specific flags and parameters
- `INSTRUCTIONS` is the natural language description of what you want to accomplish

### Developer Agent (dev)

The developer agent helps you create and manage complete projects. It can:
- Set up project structure
- Install dependencies
- Create and modify files
- Run commands

**Example 1: Create a Flask REST API with database**
```bash
python src/main.py dev "Create a Flask API with SQLAlchemy integration, JWT authentication, and endpoints for user registration, login, and profile management."
```

**Example 2: Configure a project with specific packages**
```bash
python src/main.py dev "Set up a Django project with Django REST framework, Celery for task queue, and PostgreSQL configuration."
```

### Code Generation (code)

The code generation command creates specific files based on your instructions.

**Example 1: Generate a utility function**
```bash
python src/main.py code "Create a utility module with functions for data validation including email, phone numbers, and credit cards" --file utils/validators.py
```

**Example 2: Create a complex class**
```bash
python src/main.py code "Create a ThreadPool class that manages a pool of worker threads for parallel task execution with proper error handling and results collection" --file utils/thread_pool.py
```

**Example 3: Generate in a specific language**
```bash
python src/main.py code "Create a linked list implementation with methods for insertion, deletion, and traversal" --file linked_list.js --language javascript
```

### Cursor Integration (cursor)

The cursor command interacts directly with the Cursor IDE.

**Example 1: Code refactoring**
```bash
python src/main.py cursor "Open file app.py and refactor the authentication function to use JWT tokens instead of sessions"
```

**Example 2: Create and run tests**
```bash
python src/main.py cursor "Create unit tests for all functions in utils.py and run them"
```

**Example 3: Add documentation**
```bash
python src/main.py cursor "Add proper docstrings to all functions in the models directory following the Google Python style guide"
```

### General Tasks (task)

The task command routes your request to the most appropriate agent based on complexity and requirements.

**Example 1: Create a complete feature**
```bash
python src/main.py task "Add password reset functionality to my Flask application, including email sending, token generation, and frontend forms"
```

**Example 2: Debug an issue**
```bash
python src/main.py task "My React component isn't rendering properly when I pass the following props... Help me debug and fix it"
```

**Example 3: Refactor code**
```bash
python src/main.py task "Refactor my Redux store to use Redux Toolkit and implement proper slicing of the state"
```

### Server Mode

Server mode allows you to run the agent as a service and send tasks via HTTP requests.

**Starting the server**:
```bash
python src/main.py server --port 8080
```

**Sending tasks from different sources**:

1. Using curl:
```bash
curl -X POST http://localhost:8080/execute \
  -H "Content-Type: application/json" \
  -d '{"task": "Create a React component for displaying paginated data from an API"}'
```

2. Using Python requests:
```python
import requests
response = requests.post(
    "http://localhost:8080/execute",
    json={"task": "Create an authentication middleware for Express.js"}
)
print(response.json())
```

3. From a web application:
```javascript
fetch('http://localhost:8080/execute', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    task: 'Create a utility function for formatting dates in different locales'
  }),
})
.then(response => response.json())
.then(data => console.log(data));
```

### Workflow Examples

#### Example 1: Full-Stack Feature Development

1. Create the backend API endpoints:
```bash
python src/main.py task "Create REST API endpoints for a blog post feature using Express and MongoDB"
```

2. Generate the frontend components:
```bash
python src/main.py code "Create a React component for displaying and editing blog posts" --file src/components/BlogPost.jsx --language javascript
```

3. Write tests for the API:
```bash
python src/main.py task "Write Jest tests for the blog post API endpoints"
```

#### Example 2: Project Bootstrap

1. Set up the project structure:
```bash
python src/main.py dev "Create a Python CLI tool with Click for argument parsing, proper package structure, and logging"
```

2. Add core functionality:
```bash
python src/main.py task "Implement the core functionality to scrape data from websites and export to CSV and JSON formats"
```

3. Create documentation:
```bash
python src/main.py cursor "Generate README.md documentation with installation and usage instructions"
```

### Tips for Effective Prompts

1. **Be specific about requirements**:
   - Good: "Create a function to validate email addresses with RFC 5322 compliance"
   - Less effective: "Make an email validator"

2. **Include context when necessary**:
   - Good: "My project uses React 18 with TypeScript. Create a custom hook for handling form state."
   - Less effective: "Create a form hook"

3. **Specify output format if important**:
   - Good: "Generate a user authentication module using JWT tokens and return appropriate HTTP status codes for each outcome"
   - Less effective: "Create authentication"

4. **Break complex tasks into smaller ones**:
   - Instead of one giant task, chain together focused tasks for better results

### Using with Local LLMs

For privacy or to reduce costs, you can run tasks using local LLMs through LM Studio:

1. Make sure LM Studio is running and the server is started
2. Ensure your .env has the correct LLM_STUDIO_API_URL and model name
3. For lightweight tasks:
```bash
# This explicitly sets task complexity to "low" to use local LLM
export DEFAULT_COMPLEXITY=low
python src/main.py code "Create a simple function to calculate factorial" --file math_utils.py
```

### Integration with Other Tools

#### Git Workflows

You can incorporate Agents CLI into git hooks or workflows:

```bash
# Example pre-commit hook that asks the agent to review your changes
git diff --cached | python src/main.py task "Review these changes and suggest improvements"
```

#### CI/CD Pipelines

In a CI/CD pipeline script:

```bash
# Generate unit tests for new code
python src/main.py task "Generate unit tests for all functions without existing tests in the src directory"
```

#### Combined with Cron Jobs

Set up automated tasks:

```bash
# Add to crontab to run daily code quality checks
0 0 * * * cd /path/to/project && python src/main.py task "Check for code smells and suggest refactoring in files modified in the last 24 hours" > /path/to/reports/daily_code_review.txt
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
