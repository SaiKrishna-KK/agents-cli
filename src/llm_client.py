# src/llm_client.py
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY")
)

def ask_llm(system_prompt, user_prompt, model="gpt-4", temperature=0.2):
    """
    Send a conversation (system and user messages) to the LLM and return the assistant's reply.
    """
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=temperature
    )
    # Extract and return the assistant's message content
    return completion.choices[0].message["content"]

if __name__ == "__main__":
    # Quick test
    system = "You are a helpful assistant."
    user = "Write a haiku about recursion in programming."
    response = ask_llm(system, user)
    print(response)