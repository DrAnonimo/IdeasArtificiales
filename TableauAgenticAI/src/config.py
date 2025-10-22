import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from tavily import TavilyClient


load_dotenv()


@dataclass
class Settings:
    openai_api_key: str
    tavily_api_key: str
    model_name: str = os.getenv("MODEL_NAME", "gpt-4o-mini")
    max_tokens: int = int(os.getenv("MAX_TOKENS", "800"))
    temperature: float = float(os.getenv("TEMPERATURE", "0.3"))


def get_settings() -> Settings:
    openai_key = os.getenv("OPENAI_API_KEY")
    tavily_key = os.getenv("TAVILY_API_KEY")
    if not openai_key:
        raise RuntimeError("OPENAI_API_KEY is not set. Please set it in your environment or .env file")
    if not tavily_key:
        raise RuntimeError("TAVILY_API_KEY is not set. Please set it in your environment or .env file")
    return Settings(openai_api_key=openai_key, tavily_api_key=tavily_key)


def make_llm(settings: Optional[Settings] = None) -> ChatOpenAI:
    s = settings or get_settings()
    try:
        return ChatOpenAI(
            model=s.model_name, 
            temperature=s.temperature, 
            max_tokens=s.max_tokens, 
            api_key=s.openai_api_key
        )
    except Exception as e:
        # Fallback for version compatibility issues
        try:
            return ChatOpenAI(
                model=s.model_name, 
                temperature=s.temperature, 
                max_tokens=s.max_tokens, 
                openai_api_key=s.openai_api_key
            )
        except Exception as e2:
            raise RuntimeError(f"Failed to initialize OpenAI client: {str(e)}. Also tried alternative parameter name: {str(e2)}")


def make_tavily(settings: Optional[Settings] = None) -> TavilyClient:
    s = settings or get_settings()
    return TavilyClient(api_key=s.tavily_api_key)
