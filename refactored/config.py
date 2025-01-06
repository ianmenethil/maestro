# F:\_AI\MCPServer\maestro\refactored\config.py
import os


def get_required_api_key(name: str) -> str:
    """Get API key with validation."""
    key = os.environ.get(f"{name.upper()}_API_KEY")
    if not key:
        raise ValueError(f"Missing required API key: {name.upper()}_API_KEY")
    return key


# Model configurations
MODEL_CONFIGS = {
    "orchestrator": {
        "model": "gemini/gemini-1.5-flash-latest",
        "max_tokens": 4000,
        "timeout": 30
    },
    "sub_agent": {
        "model": "openai/gpt-4o-mini",
        "max_tokens": 4000,
        "timeout": 30
    },
    "refiner": {
        "model": "gemini/gemini-1.5-flash-latest",
        "max_tokens": 4000,
        "timeout": 30
    }
}

# API Keys with validation
OPENAI_API_KEY: str = get_required_api_key("openai")
ANTHROPIC_API_KEY: str = get_required_api_key("anthropic")
GEMINI_API_KEY: str = get_required_api_key("gemini")
TAVILY_API_KEY: str = get_required_api_key("tavily")
# Models with easy access
ORCHESTRATOR_MODEL = MODEL_CONFIGS["orchestrator"]["model"]
SUB_AGENT_MODEL = MODEL_CONFIGS["sub_agent"]["model"]
REFINER_MODEL = MODEL_CONFIGS["refiner"]["model"]
