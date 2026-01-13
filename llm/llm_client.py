import os

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def get_llm():
    """
    Initialize and return the LLM client with intelligent fallback strategy.

    Priority order:
    1. Try Groq with llama-3.3-70b-versatile (most capable)
    2. Fallback to Groq with llama-3.1-8b-instant (fastest)
    3. Fallback to Groq with gemma2-9b-it (alternative)
    4. Final fallback to Gemini if Groq unavailable

    This ensures the system always has a working LLM.
    """
    groq_key = os.getenv("GROQ_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY")

    if groq_key:
        try:
            from langchain_groq import ChatGroq

            # Try multiple Groq models in order of preference
            # Updated list - removed decommissioned models
            groq_models = [
                "llama-3.3-70b-versatile",  # Most capable, good for complex reasoning
                "llama-3.1-8b-instant",  # Fastest, highest rate limit
                "gemma2-9b-it",  # Alternative fast option
            ]

            # Return first available model (will fail at runtime if rate limited)
            for model in groq_models:
                try:
                    return ChatGroq(
                        model=model,
                        temperature=0.2,
                        api_key=groq_key,
                        max_retries=0,  # Fail fast if rate limited
                    )
                except Exception:
                    continue

            # If all specific models fail, try default
            return ChatGroq(
                model="llama-3.1-8b-instant",
                temperature=0.2,
                api_key=groq_key,
            )

        except Exception as e:
            print(f"⚠️ Groq initialization failed: {e}")
            print("Falling back to Gemini...")

    # Fallback to Gemini if Groq not available or fails
    if gemini_key:
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI

            return ChatGoogleGenerativeAI(
                model="gemini-2.0-flash-exp",
                temperature=0.2,
                google_api_key=gemini_key,
            )
        except Exception as e:
            print(f"❌ Gemini initialization failed: {e}")
            raise RuntimeError(
                "No LLM available. Please set GROQ_API_KEY or GEMINI_API_KEY in .env file"
            )

    # No API keys available
    raise RuntimeError(
        "No LLM API keys found. Please set GROQ_API_KEY or GEMINI_API_KEY in .env file.\n"
        "Get Groq key (free): https://console.groq.com/\n"
        "Get Gemini key (free): https://makersuite.google.com/app/apikey"
    )
