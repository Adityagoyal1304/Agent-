"""
llm.py — Single source of truth for the chat model.

Keeping the provider behind one function means we can swap Gemini → GPT-4o
by changing one env var, with zero changes to node code.
"""

import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI


def get_llm():
    """Return a LangChain chat model configured from environment variables."""
    # Always reload .env with override=True so updating the key in .env works immediately without restarting uvicorn
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"), override=True)
    api_key = os.getenv("GEMINI_API_KEY", "")
    model_name = os.getenv("MODEL_NAME", "gemini-flash-latest")
    return ChatGoogleGenerativeAI(
        model=model_name,
        google_api_key=api_key,
        temperature=0.2,      # Low temperature: we want consistent, structured output
        max_retries=3,
    )
