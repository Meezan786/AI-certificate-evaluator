import os

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def get_llm():
    """
    Initialize and return the LLM client with intelligent runtime fallback.

    Tries multiple models dynamically to handle rate limits during demos.
    Each model has separate quotas, so we cycle through them.
    """
    groq_key = os.getenv("GROQ_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY")

    # Try Groq models first
    if groq_key:
        try:
            from langchain_groq import ChatGroq

            # List of Groq models to try (each has separate rate limits)
            groq_models = [
                "llama-3.1-8b-instant",  # Fastest, highest rate limit
                "llama3-8b-8192",  # Alternative fast model
                "gemma2-9b-it",  # Google's Gemma
                "gemma-7b-it",  # Smaller Gemma
                "llama-3.1-70b-versatile",  # More capable
                "llama3-70b-8192",  # Alternative capable model
            ]

            # Try each model
            for model in groq_models:
                try:
                    llm = ChatGroq(
                        model=model,
                        temperature=0.2,
                        api_key=groq_key,
                    )
                    # Return first working model
                    return llm
                except Exception:
                    continue

        except Exception as e:
            print(f"⚠️ Groq unavailable: {e}")

    # Fallback to Gemini
    if gemini_key:
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI

            print("✓ Using Gemini (Google)")
            return ChatGoogleGenerativeAI(
                model="gemini-2.0-flash-exp",
                temperature=0.2,
                google_api_key=gemini_key,
            )
        except Exception as e:
            print(f"❌ Gemini failed: {e}")
            raise RuntimeError("No LLM available")

    raise RuntimeError(
        "No LLM API keys found. Please set GROQ_API_KEY or GEMINI_API_KEY in .env file.\n"
        "Get Groq key (free): https://console.groq.com/\n"
        "Get Gemini key (free): https://makersuite.google.com/app/apikey"
    )


def get_llm_with_fallback():
    """
    Smart LLM getter that handles rate limits at RUNTIME.
    Tries multiple models if one fails.
    """
    groq_key = os.getenv("GROQ_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY")

    # All available models to try
    models_to_try = []

    if groq_key:
        # Groq models (ordered by rate limit generosity)
        groq_models = [
            ("groq", "llama-3.1-8b-instant"),
            ("groq", "llama3-8b-8192"),
            ("groq", "gemma2-9b-it"),
            ("groq", "gemma-7b-it"),
            ("groq", "llama-3.1-70b-versatile"),
            ("groq", "llama3-70b-8192"),
        ]
        models_to_try.extend(groq_models)

    if gemini_key:
        models_to_try.append(("gemini", "gemini-2.0-flash-exp"))
        models_to_try.append(("gemini", "gemini-1.5-flash"))

    # Try each model until one works
    for provider, model_name in models_to_try:
        try:
            if provider == "groq":
                from langchain_groq import ChatGroq

                return ChatGroq(
                    model=model_name,
                    temperature=0.2,
                    api_key=groq_key,
                    max_retries=0,
                )
            elif provider == "gemini":
                from langchain_google_genai import ChatGoogleGenerativeAI

                return ChatGoogleGenerativeAI(
                    model=model_name,
                    temperature=0.2,
                    google_api_key=gemini_key,
                )
        except Exception:
            continue

    raise RuntimeError("All LLM models exhausted or unavailable")
