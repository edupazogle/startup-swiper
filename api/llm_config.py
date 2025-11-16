"""
LiteLLM Configuration and Logging Module with NVIDIA NIM Support

This module configures LiteLLM with:
- Debugging enabled
- NVIDIA NIM support for DeepSeek models
- All LLM requests and responses logged to /logs/llm folder
- Environment-based model selection
- LangSmith tracing integration
"""

import os
import json
import litellm
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
import asyncio
from functools import wraps
from dotenv import load_dotenv
from langsmith import traceable

# Load environment variables from multiple possible locations
env_paths = [
    Path(__file__).parent / ".env",
    Path(__file__).parent.parent / "app" / "startup-swipe-schedu" / ".env",
    Path(__file__).parent.parent / ".env",
]
for env_path in env_paths:
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✓ Loaded environment from: {env_path}")
        break

# Configure LiteLLM
litellm.set_verbose = True  # Enable verbose logging
litellm.success_callback = []
litellm.failure_callback = []

# Set up logs directory
LOGS_DIR = Path(__file__).parent.parent / "logs" / "llm"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# ====================
# NVIDIA NIM Configuration
# ====================
# NVIDIA NIM (NVIDIA Inference Microservices) provides optimized inference
# for various open-source models. LiteLLM supports NIM through custom endpoints.

NVIDIA_NIM_CONFIG = {
    "api_key": os.getenv("NVIDIA_API_KEY"),
    "base_url": os.getenv("NVIDIA_NIM_BASE_URL", "https://integrate.api.nvidia.com/v1"),
    "default_model": os.getenv("NVIDIA_DEFAULT_MODEL", "qwen/qwen3-next-80b-a3b-instruct"),
    "embedding_model": os.getenv("NVIDIA_EMBEDDING_MODEL", "nvidia/llama-3.2-nemoretriever-300m-embed-v2"),
}

# Validate NVIDIA NIM configuration
if NVIDIA_NIM_CONFIG["api_key"]:
    print(f"✓ NVIDIA NIM configured:")
    print(f"  - API Key: {'*' * 20}...")
    print(f"  - Base URL: {NVIDIA_NIM_CONFIG['base_url']}")
    print(f"  - Default Model: {NVIDIA_NIM_CONFIG['default_model']}")
    print(f"  - Embedding Model: {NVIDIA_NIM_CONFIG['embedding_model']}")
else:
    print("⚠️  NVIDIA_API_KEY not set. NVIDIA NIM features will not work.")

class LLMLogger:
    """Logger for LLM requests and responses"""
    
    def __init__(self, log_dir: Path = LOGS_DIR):
        self.log_dir = log_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_log_filename(self, model: str, request_id: str) -> str:
        """Generate a unique filename for the log"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        safe_model = model.replace("/", "_").replace(":", "_")
        return f"{timestamp}_{safe_model}_{request_id[:8]}.json"
    
    def log_request_response(
        self,
        model: str,
        messages: List[Dict[str, Any]],
        response: Any,
        request_id: str,
        duration_ms: float,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Log a complete LLM request and response"""
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "request_id": request_id,
            "model": model,
            "duration_ms": duration_ms,
            "request": {
                "messages": messages,
                "metadata": metadata or {}
            },
            "response": None,
            "error": error,
            "success": error is None
        }
        
        # Extract response data
        if response and not error:
            try:
                if hasattr(response, 'choices') and len(response.choices) > 0:
                    log_data["response"] = {
                        "content": response.choices[0].message.content,
                        "role": response.choices[0].message.role,
                        "finish_reason": response.choices[0].finish_reason,
                        "usage": {
                            "prompt_tokens": response.usage.prompt_tokens if hasattr(response, 'usage') else None,
                            "completion_tokens": response.usage.completion_tokens if hasattr(response, 'usage') else None,
                            "total_tokens": response.usage.total_tokens if hasattr(response, 'usage') else None
                        },
                        "model": response.model if hasattr(response, 'model') else model,
                        "id": response.id if hasattr(response, 'id') else None
                    }
                elif isinstance(response, str):
                    log_data["response"] = {
                        "content": response,
                        "type": "string_response"
                    }
            except Exception as e:
                log_data["response"] = {
                    "error": f"Failed to extract response data: {str(e)}",
                    "raw": str(response)
                }
        
        # Write to file
        filename = self._get_log_filename(model, request_id)
        log_path = self.log_dir / filename
        
        try:
            with open(log_path, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, indent=2, ensure_ascii=False)
            print(f"✓ LLM log saved: {filename}")
        except Exception as e:
            print(f"✗ Failed to save LLM log: {e}")
    
    def log_streaming_response(
        self,
        model: str,
        messages: List[Dict[str, Any]],
        chunks: List[str],
        request_id: str,
        duration_ms: float,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Log a streaming LLM response"""
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "request_id": request_id,
            "model": model,
            "duration_ms": duration_ms,
            "streaming": True,
            "request": {
                "messages": messages,
                "metadata": metadata or {}
            },
            "response": {
                "chunks": chunks,
                "full_content": "".join(chunks),
                "num_chunks": len(chunks)
            },
            "success": True
        }
        
        filename = self._get_log_filename(model, request_id)
        log_path = self.log_dir / filename
        
        try:
            with open(log_path, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, indent=2, ensure_ascii=False)
            print(f"✓ LLM streaming log saved: {filename}")
        except Exception as e:
            print(f"✗ Failed to save LLM streaming log: {e}")


# Global logger instance
llm_logger = LLMLogger()


def generate_request_id() -> str:
    """Generate a unique request ID"""
    import uuid
    return str(uuid.uuid4())


@traceable(
    name="llm_completion",
    run_type="llm",
    tags=["llm", "completion"]
)
async def llm_completion(
    messages: List[Dict[str, Any]],
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
    stream: bool = False,
    metadata: Optional[Dict[str, Any]] = None,
    use_nvidia_nim: bool = True,
    tools: Optional[List[Dict[str, Any]]] = None,
    tool_choice: Optional[str] = None,
    **kwargs
) -> Any:
    """
    Make an LLM completion request with logging and NVIDIA NIM support

    Args:
        messages: List of message dictionaries with 'role' and 'content'
        model: Model name (supports OpenAI, Anthropic, NVIDIA NIM, etc. via LiteLLM)
               If None and use_nvidia_nim=True, uses NVIDIA_DEFAULT_MODEL
        temperature: Sampling temperature
        max_tokens: Maximum tokens to generate
        stream: Whether to stream the response (not supported in this version)
        metadata: Additional metadata to log
        use_nvidia_nim: If True and no model specified, use NVIDIA NIM default model
        tools: List of tool definitions for function calling (OpenAI format)
        tool_choice: Control which tool the model should use ("auto", "none", or specific tool)
        **kwargs: Additional arguments to pass to LiteLLM

    Returns:
        LLM response object or string
    """
    request_id = generate_request_id()
    start_time = datetime.now()
    
    # Use NVIDIA NIM model if no model specified and enabled
    if model is None and use_nvidia_nim and NVIDIA_NIM_CONFIG["api_key"]:
        model = NVIDIA_NIM_CONFIG["default_model"]
    elif model is None:
        model = "gpt-4o"
    
    # Configure NVIDIA NIM headers if using NIM model
    if use_nvidia_nim and NVIDIA_NIM_CONFIG["api_key"]:
        if "nvidia" in model.lower() or "deepseek" in model.lower() or "qwen" in model.lower():
            kwargs.setdefault("api_key", NVIDIA_NIM_CONFIG["api_key"])
            kwargs.setdefault("api_base", NVIDIA_NIM_CONFIG["base_url"])
            # When using api_base, use openai/ prefix for compatibility or just the model name
            # LiteLLM will route to the custom endpoint
            if model.startswith("nvidia/"):
                # Remove nvidia/ prefix when using custom api_base
                model = model.replace("nvidia/", "")
            # Use openai compatibility mode for custom endpoints
            if not model.startswith("openai/"):
                model = f"openai/{model}"
    elif use_nvidia_nim and not NVIDIA_NIM_CONFIG["api_key"]:
        # Fall back to GPT-4o if NVIDIA NIM is requested but no API key is set
        if "deepseek" in model.lower() or "qwen" in model.lower():
            model = "gpt-4o"

    try:
        # Make the LLM call (non-streaming only for now)
        call_kwargs = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,  # Force non-streaming to avoid async generator issue
            **kwargs
        }
        
        # Add tools if provided
        if tools:
            call_kwargs["tools"] = tools
            if tool_choice:
                call_kwargs["tool_choice"] = tool_choice
        
        response = await litellm.acompletion(**call_kwargs)

        end_time = datetime.now()
        duration_ms = (end_time - start_time).total_seconds() * 1000

        # Log regular response
        llm_logger.log_request_response(
            model=model,
            messages=messages,
            response=response,
            request_id=request_id,
            duration_ms=duration_ms,
            metadata=metadata
        )

        return response

    except Exception as e:
        end_time = datetime.now()
        duration_ms = (end_time - start_time).total_seconds() * 1000

        # Log the error
        llm_logger.log_request_response(
            model=model,
            messages=messages,
            response=None,
            request_id=request_id,
            duration_ms=duration_ms,
            error=str(e),
            metadata=metadata
        )

        raise


def llm_completion_sync(
    messages: List[Dict[str, Any]],
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
    metadata: Optional[Dict[str, Any]] = None,
    use_nvidia_nim: bool = True,
    **kwargs
) -> Any:
    """
    Synchronous wrapper for LLM completion with logging and NVIDIA NIM support
    
    Args:
        messages: List of message dictionaries with 'role' and 'content'
        model: Model name (if None and use_nvidia_nim=True, uses NVIDIA default)
        temperature: Sampling temperature
        max_tokens: Maximum tokens to generate
        metadata: Additional metadata to log
        use_nvidia_nim: If True and no model specified, use NVIDIA NIM default model
        **kwargs: Additional arguments to pass to LiteLLM
    """
    request_id = generate_request_id()
    start_time = datetime.now()
    
    # Use NVIDIA NIM model if no model specified and enabled
    if model is None and use_nvidia_nim and NVIDIA_NIM_CONFIG["api_key"]:
        model = NVIDIA_NIM_CONFIG["default_model"]
    elif model is None:
        model = "gpt-4o"
    
    # Format model for NVIDIA NIM
    if use_nvidia_nim and NVIDIA_NIM_CONFIG["api_key"]:
        if "deepseek" in model.lower() or "nvidia" in model.lower() or "qwen" in model.lower():
            # Set base URL and API key for NVIDIA NIM
            kwargs.setdefault("api_key", NVIDIA_NIM_CONFIG["api_key"])
            kwargs.setdefault("api_base", NVIDIA_NIM_CONFIG["base_url"])
            # When using api_base, use openai/ prefix for compatibility
            if model.startswith("nvidia/"):
                model = model.replace("nvidia/", "")
            if not model.startswith("openai/"):
                model = f"openai/{model}"
    elif use_nvidia_nim and not NVIDIA_NIM_CONFIG["api_key"]:
        # Fall back to GPT-4o if NVIDIA NIM is requested but no API key is set
        if "deepseek" in model.lower() or "qwen" in model.lower():
            model = "gpt-4o"
    
    try:
        # Make the LLM call
        response = litellm.completion(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        
        end_time = datetime.now()
        duration_ms = (end_time - start_time).total_seconds() * 1000
        
        # Log response
        llm_logger.log_request_response(
            model=model,
            messages=messages,
            response=response,
            request_id=request_id,
            duration_ms=duration_ms,
            metadata=metadata
        )
        
        return response
        
    except Exception as e:
        end_time = datetime.now()
        duration_ms = (end_time - start_time).total_seconds() * 1000
        
        # Log the error
        llm_logger.log_request_response(
            model=model,
            messages=messages,
            response=None,
            request_id=request_id,
            duration_ms=duration_ms,
            error=str(e),
            metadata=metadata
        )
        
        raise


def simple_llm_call(
    prompt: str,
    model: Optional[str] = None,
    system_message: Optional[str] = None,
    temperature: float = 0.7,
    use_nvidia_nim: bool = True,
    **kwargs
) -> str:
    """
    Simple synchronous LLM call that returns just the text content
    
    Args:
        prompt: User prompt
        model: Model name (if None and use_nvidia_nim=True, uses NVIDIA default)
        system_message: Optional system message
        temperature: Sampling temperature
        use_nvidia_nim: If True and no model specified, use NVIDIA NIM default model
        **kwargs: Additional arguments
    
    Returns:
        String response from the LLM
    """
    messages = []
    
    if system_message:
        messages.append({"role": "system", "content": system_message})
    
    messages.append({"role": "user", "content": prompt})
    
    response = llm_completion_sync(
        messages=messages,
        model=model,
        temperature=temperature,
        use_nvidia_nim=use_nvidia_nim,
        **kwargs
    )
    
    if hasattr(response, 'choices') and len(response.choices) > 0:
        return response.choices[0].message.content
    
    return str(response)


async def simple_llm_call_async(
    prompt: str,
    model: Optional[str] = None,
    system_message: Optional[str] = None,
    temperature: float = 0.7,
    use_nvidia_nim: bool = True,
    **kwargs
) -> str:
    """
    Simple async LLM call that returns just the text content
    
    Args:
        prompt: User prompt
        model: Model name (if None and use_nvidia_nim=True, uses NVIDIA default)
        system_message: Optional system message
        temperature: Sampling temperature
        use_nvidia_nim: If True and no model specified, use NVIDIA NIM default model
        **kwargs: Additional arguments
    
    Returns:
        String response from the LLM
    """
    messages = []
    
    if system_message:
        messages.append({"role": "system", "content": system_message})
    
    messages.append({"role": "user", "content": prompt})
    
    response = await llm_completion(
        messages=messages,
        model=model,
        temperature=temperature,
        use_nvidia_nim=use_nvidia_nim,
        **kwargs
    )
    
    if hasattr(response, 'choices') and len(response.choices) > 0:
        return response.choices[0].message.content
    
    return str(response)


# Environment variable configuration
def configure_llm_api_keys():
    """
    Configure API keys from environment variables
    
    Set these in your .env file or environment:
    - OPENAI_API_KEY (for GPT models)
    - ANTHROPIC_API_KEY (for Claude models)
    - AZURE_API_KEY (for Azure OpenAI)
    - NVIDIA_API_KEY (for NVIDIA NIM models)
    - NVIDIA_NIM_BASE_URL (optional, defaults to https://integrate.api.nvidia.com/v1)
    - NVIDIA_DEFAULT_MODEL (optional, defaults to deepseek-ai/deepseek-r1)
    """
    # LiteLLM automatically reads from standard environment variables
    # NVIDIA NIM API key is already configured above
    pass


def get_nvidia_nim_model() -> str:
    """Get the configured NVIDIA NIM model name"""
    return NVIDIA_NIM_CONFIG["default_model"]


def get_nvidia_nim_embedding_model() -> str:
    """Get the configured NVIDIA NIM embedding model name"""
    return NVIDIA_NIM_CONFIG["embedding_model"]


def is_nvidia_nim_configured() -> bool:
    """Check if NVIDIA NIM is properly configured"""
    return bool(NVIDIA_NIM_CONFIG["api_key"])


# Initialize on import
configure_llm_api_keys()

print(f"✓ LiteLLM configured with logging to: {LOGS_DIR}")
if is_nvidia_nim_configured():
    print(f"✓ NVIDIA NIM support enabled (Model: {get_nvidia_nim_model()})")
