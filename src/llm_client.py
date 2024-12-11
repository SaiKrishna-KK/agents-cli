# src/llm_client.py
import os
import openai

openai.api_key = os.environ.get("OPENAI_API_KEY")

def ask_llm(system_prompt, user_prompt, model="gpt-3.5-turbo", temperature=0.2):
    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=temperature
    )
    return response.choices[0].message["content"]
