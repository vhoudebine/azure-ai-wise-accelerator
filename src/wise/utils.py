import os
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()

def get_chat_completion(aoai_client, 
                        messages, 
                        temperature=0, 
                        max_tokens=8000, 
                        model=os.getenv("AZURE_OPENAI_GPT4O_DEPLOYMENT"),
                        response_format=None
                        ):
    try:
        response = aoai_client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format=response_format
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"An error occurred: {e}")
        return None