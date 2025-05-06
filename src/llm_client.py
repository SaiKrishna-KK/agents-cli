# src/llm_client.py
import os
import re
import json
import requests
from dotenv import load_dotenv
try:
    from openai import OpenAI
except ImportError:
    print("OpenAI package not installed properly. Using mock responses.")
    OpenAI = None

load_dotenv()

USE_MOCK = os.getenv("USE_MOCK_RESPONSES", "false").lower() == "true"

# Try to initialize clients, but allow for missing keys for testing
try:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    if OPENAI_API_KEY and not USE_MOCK and OpenAI:
        openai_client = OpenAI(api_key=OPENAI_API_KEY)
    else:
        openai_client = None
except Exception as e:
    print(f"Error initializing OpenAI client: {str(e)}")
    openai_client = None

# LM Studio configuration
LLM_STUDIO_API_URL = os.getenv("LLM_STUDIO_API_URL", "http://localhost:8000/v1")
LLM_STUDIO_API_KEY = os.getenv("LLM_STUDIO_API_KEY", "")
DEFAULT_LOCAL_MODEL = os.getenv("DEFAULT_LOCAL_MODEL", "default")
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY", "")

# Initialize LM Studio client if OpenAI SDK is available
try:
    if OpenAI and not USE_MOCK:
        lm_studio_client = OpenAI(base_url=LLM_STUDIO_API_URL, api_key=LLM_STUDIO_API_KEY or "lm-studio")
    else:
        lm_studio_client = None
except Exception as e:
    print(f"Error initializing LM Studio client: {str(e)}")
    lm_studio_client = None

# Mock responses for testing
MOCK_RESPONSES = {
    "developer": """{
        "steps": [
            {"action": "create_venv", "path": "./venv"},
            {"action": "install_deps", "deps": ["flask", "pytest", "requests"]},
            {"action": "create_file", "path": "app.py", "content": "from flask import Flask, jsonify\\n\\napp = Flask(__name__)\\n\\n@app.route('/hello', methods=['GET'])\\ndef hello():\\n    return jsonify({\\\"message\\\": \\\"Hello, World!\\\"})\\n\\nif __name__ == '__main__':\\n    app.run(host='0.0.0.0', port=5000)\\n"},
            {"action": "create_file", "path": "test_app.py", "content": "import pytest\\nimport requests\\n\\ndef test_hello_endpoint():\\n    response = requests.get('http://localhost:5000/hello')\\n    assert response.status_code == 200\\n    assert response.json() == {\\\"message\\\": \\\"Hello, World!\\\"}\\n"},
            {"action": "run_command", "command": "python app.py", "background": true},
            {"action": "run_command", "command": "pytest test_app.py -v", "background": false},
            {"action": "kill_process"}
        ]
    }""",
    "tester": """{
        "steps": [
            {"action": "install_deps", "deps": ["requests"]}
        ]
    }""",
    "debugger": """{
        "steps": [
            {"action": "modify_file", "path": "app.py", "content": "from flask import Flask, jsonify\\n\\napp = Flask(__name__)\\n\\n@app.route('/hello', methods=['GET'])\\ndef hello():\\n    return jsonify({\\\"message\\\": \\\"Hello, World!\\\"})\\n\\nif __name__ == '__main__':\\n    app.run(host='0.0.0.0', port=5000, debug=False)\\n"}
        ]
    }""",
    "code_generation": """def parse_csv(file_path):
    \"\"\"
    Parse a CSV file and return the data as a list of dictionaries.
    
    Args:
        file_path: Path to the CSV file
        
    Returns:
        List of dictionaries, where each dictionary represents a row in the CSV
    \"\"\"
    import csv
    
    data = []
    try:
        with open(file_path, 'r', newline='', encoding='utf-8') as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                data.append(row)
        return data
    except Exception as e:
        print(f"Error parsing CSV file: {str(e)}")
        return []
""",
    "email_validator": """def validate_email(email):
    \"\"\"
    Validate an email address format.
    
    Args:
        email: Email address to validate
        
    Returns:
        bool: True if valid, False otherwise
    \"\"\"
    import re
    
    if not email or not isinstance(email, str):
        return False
        
    # Regular expression for validating an Email
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    # Check if the email matches the pattern
    if re.match(pattern, email):
        return True
    return False
""",
    "cursor": """{
        "actions": [
            {"type": "create_file", "path": "hello.py", "content": "print('Hello, world!')"},
            {"type": "run_terminal", "command": "python hello.py"}
        ]
    }""",
    "router": """{
        "route_to": "local",
        "complexity": "low",
        "explanation": "Simple task that can be handled by a local LLM"
    }""",
    "task_analysis": """{
        "complexity": "low",
        "agent": "code_generation",
        "instructions": "Generate a function to validate email addresses",
        "file_paths": ["email_validator.py"],
        "language": "python"
    }"""
}

def get_mock_response(prompt_type):
    """Get a mock response for testing."""
    if prompt_type in MOCK_RESPONSES:
        return MOCK_RESPONSES[prompt_type]
    
    # Default mock response
    if "developer" in prompt_type.lower():
        return MOCK_RESPONSES["developer"]
    elif "test" in prompt_type.lower():
        return MOCK_RESPONSES["tester"]
    elif "debug" in prompt_type.lower():
        return MOCK_RESPONSES["debugger"]
    elif "code" in prompt_type.lower():
        return MOCK_RESPONSES["code_generation"]
    elif "cursor" in prompt_type.lower():
        return MOCK_RESPONSES["cursor"]
    elif "route" in prompt_type.lower():
        return MOCK_RESPONSES["router"]
    elif "task" in prompt_type.lower():
        return MOCK_RESPONSES["task_analysis"]
    elif "email" in prompt_type.lower():
        return MOCK_RESPONSES["email_validator"]
    else:
        return MOCK_RESPONSES["developer"]

def check_lm_studio_health():
    """Check if LM Studio API is accessible and get available models."""
    if USE_MOCK:
        return True, ["mock-model"]
        
    try:
        url = f"{LLM_STUDIO_API_URL.rstrip('/v1')}/v1/models"
        response = requests.get(url)
        if response.status_code == 200:
            models = response.json().get("data", [])
            return True, [model.get("id") for model in models]
        else:
            return False, f"Error: {response.status_code}, {response.text}"
    except Exception as e:
        return False, f"Error connecting to LM Studio: {str(e)}"

def ask_llm(system_prompt, user_prompt, model="gpt-4", temperature=0.2, use_local=False, task_complexity="low"):
    """
    Send a prompt to either OpenAI, Anthropic (Claude), or a local LLM Studio model based on complexity.
    
    Args:
        system_prompt: The system instructions
        user_prompt: The user query
        model: Model identifier
        temperature: Temperature parameter for response generation
        use_local: Whether to use local LLM Studio API
        task_complexity: "low", "medium", or "high" to determine which LLM to use
    """
    # For testing, use mock responses based on the system prompt
    if USE_MOCK:
        # Identify prompt type
        if "Developer Agent" in system_prompt:
            return get_mock_response("developer")
        elif "Tester Agent" in system_prompt:
            return get_mock_response("tester")
        elif "Debugger Agent" in system_prompt:
            return get_mock_response("debugger")
        elif "expert" in system_prompt and "developer" in system_prompt:
            if "email" in user_prompt.lower():
                return get_mock_response("email_validator")
            return get_mock_response("code_generation")
        elif "controls the Cursor IDE" in system_prompt:
            return get_mock_response("cursor")
        elif "Router Agent" in system_prompt:
            return get_mock_response("router")
        elif "Task Manager Agent" in system_prompt:
            return get_mock_response("task_analysis")
        else:
            print(f"Using default mock response for unknown prompt type: {system_prompt[:50]}...")
            return get_mock_response("developer")
    
    # Route to appropriate LLM based on complexity
    if task_complexity == "high" and CLAUDE_API_KEY:
        return ask_claude(system_prompt, user_prompt, temperature=temperature)
    elif use_local or task_complexity == "low":
        return ask_local_llm(system_prompt, user_prompt, model=DEFAULT_LOCAL_MODEL, temperature=temperature)
    else:
        return ask_openai(system_prompt, user_prompt, model=model, temperature=temperature)

def ask_openai(system_prompt, user_prompt, model="gpt-4", temperature=0.2):
    """Send a prompt to OpenAI API"""
    if USE_MOCK:
        return get_mock_response("developer")
        
    if not openai_client:
        print("OpenAI client not initialized. Using mock response.")
        return get_mock_response("developer")
        
    try:
        completion = openai_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature
        )
        response = completion.choices[0].message.content
        return response
    except Exception as e:
        print(f"Error calling OpenAI API: {str(e)}")
        return get_mock_response("developer")

def ask_local_llm(system_prompt, user_prompt, model=DEFAULT_LOCAL_MODEL, temperature=0.2):
    """Send a prompt to local LLM Studio API"""
    if USE_MOCK:
        return get_mock_response("developer")
        
    # Try using the OpenAI client SDK approach first (preferred)
    if lm_studio_client:
        try:
            completion = lm_studio_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature
            )
            return completion.choices[0].message.content
        except Exception as e:
            print(f"Error using LM Studio client: {str(e)}")
            # Fall back to direct API call
    
    # Direct API call as fallback
    try:
        headers = {"Content-Type": "application/json"}
        if LLM_STUDIO_API_KEY:
            headers["Authorization"] = f"Bearer {LLM_STUDIO_API_KEY}"
            
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": temperature
        }
        
        chat_endpoint = f"{LLM_STUDIO_API_URL.rstrip('/v1')}/v1/chat/completions"
        response = requests.post(chat_endpoint, headers=headers, json=payload)
        
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            print(f"Error from local LLM API: {response.status_code}, {response.text}")
            if not USE_MOCK:
                # Fallback to OpenAI if local fails
                return ask_openai(system_prompt, user_prompt, model="gpt-3.5-turbo", temperature=temperature)
            else:
                return get_mock_response("developer")
    except Exception as e:
        print(f"Local LLM request failed: {str(e)}")
        if not USE_MOCK:
            # Fallback to OpenAI
            return ask_openai(system_prompt, user_prompt, model="gpt-3.5-turbo", temperature=temperature)
        else:
            return get_mock_response("developer")

def ask_claude(system_prompt, user_prompt, model="claude-3-sonnet-20240229", temperature=0.2):
    """Send a prompt to Anthropic's Claude API"""
    if USE_MOCK:
        return get_mock_response("developer")
        
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
        
        message = client.messages.create(
            model=model,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
            temperature=temperature
        )
        return message.content[0].text
    except Exception as e:
        print(f"Claude API request failed: {str(e)}")
        if not USE_MOCK:
            # Fallback to OpenAI
            return ask_openai(system_prompt, user_prompt, model="gpt-4", temperature=temperature)
        else:
            return get_mock_response("developer")

def get_embeddings(text_or_texts, model=DEFAULT_LOCAL_MODEL):
    """Get embeddings for text using LM Studio API.
    
    Args:
        text_or_texts: Single text string or list of text strings
        model: Model identifier for embeddings
        
    Returns:
        List of embeddings
    """
    if USE_MOCK:
        # Return mock embeddings (vectors of zeros)
        is_list = isinstance(text_or_texts, list)
        texts = text_or_texts if is_list else [text_or_texts]
        mock_embedding = [0.0] * 384  # Common embedding dimension
        
        if is_list:
            return [mock_embedding for _ in texts]
        else:
            return mock_embedding
    
    # Use the OpenAI client SDK if available
    if lm_studio_client:
        try:
            response = lm_studio_client.embeddings.create(
                model=model,
                input=text_or_texts
            )
            if isinstance(text_or_texts, list):
                return [item.embedding for item in response.data]
            else:
                return response.data[0].embedding
        except Exception as e:
            print(f"Error getting embeddings with LM Studio client: {str(e)}")
            # Fall back to direct API call
    
    # Direct API call for embeddings
    try:
        headers = {"Content-Type": "application/json"}
        if LLM_STUDIO_API_KEY:
            headers["Authorization"] = f"Bearer {LLM_STUDIO_API_KEY}"
        
        payload = {
            "model": model,
            "input": text_or_texts
        }
        
        embedding_endpoint = f"{LLM_STUDIO_API_URL.rstrip('/v1')}/v1/embeddings"
        response = requests.post(embedding_endpoint, headers=headers, json=payload)
        
        if response.status_code == 200:
            data = response.json().get("data", [])
            if isinstance(text_or_texts, list):
                return [item["embedding"] for item in data]
            else:
                return data[0]["embedding"]
        else:
            print(f"Error from embeddings API: {response.status_code}, {response.text}")
            return get_embeddings(text_or_texts, model) if USE_MOCK else None
    except Exception as e:
        print(f"Embeddings request failed: {str(e)}")
        return get_embeddings(text_or_texts, model) if USE_MOCK else None

def extract_json(response):
    match = re.search(r'\{.*\}', response, flags=re.DOTALL)
    if match:
        try:
            data = json.loads(match.group(0))
            return data
        except json.JSONDecodeError:
            # Try to fix common JSON errors
            fixed_json = fix_json_formatting(match.group(0))
            try:
                return json.loads(fixed_json)
            except json.JSONDecodeError:
                return None
    return None

def fix_json_formatting(json_str):
    """Try to fix common JSON formatting errors"""
    # Replace single quotes with double quotes
    json_str = re.sub(r"'([^']*)':", r'"\1":', json_str)
    json_str = re.sub(r": '([^']*)'", r': "\1"', json_str)
    
    # Fix trailing commas in arrays and objects
    json_str = re.sub(r",\s*}", "}", json_str)
    json_str = re.sub(r",\s*\]", "]", json_str)
    
    return json_str
