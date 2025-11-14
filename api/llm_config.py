"""
LiteLLM Configuration and Logging Module

This module configures LiteLLM with debugging enabled and saves all
LLM requests and responses to the /logs/llm folder.
"""

import os
import json
import litellm
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
import asyncio
from functools import wraps

# Configure LiteLLM
litellm.set_verbose = True  # Enable verbose logging
litellm.success_callback = []
litellm.failure_callback = []

# Set up logs directory
LOGS_DIR = Path(__file__).parent.parent / "logs" / "llm"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

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


async def llm_completion(
    messages: List[Dict[str, Any]],
    model: str = "gpt-4o",
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
    stream: bool = False,
    metadata: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Any:
    """
    Make an LLM completion request with logging

    Args:
        messages: List of message dictionaries with 'role' and 'content'
        model: Model name (supports OpenAI, Anthropic, etc. via LiteLLM)
        temperature: Sampling temperature
        max_tokens: Maximum tokens to generate
        stream: Whether to stream the response (not supported in this version)
        metadata: Additional metadata to log
        **kwargs: Additional arguments to pass to LiteLLM

    Returns:
        LLM response object or string
    """
    request_id = generate_request_id()
    start_time = datetime.now()

    try:
        # Make the LLM call (non-streaming only for now)
        response = await litellm.acompletion(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=False,  # Force non-streaming to avoid async generator issue
            **kwargs
        )

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
    model: str = "gpt-4o",
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
    metadata: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Any:
    """
    Synchronous wrapper for LLM completion with logging
    """
    request_id = generate_request_id()
    start_time = datetime.now()
    
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
    model: str = "gpt-4o",
    system_message: Optional[str] = None,
    temperature: float = 0.7,
    **kwargs
) -> str:
    """
    Simple synchronous LLM call that returns just the text content
    
    Args:
        prompt: User prompt
        model: Model name
        system_message: Optional system message
        temperature: Sampling temperature
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
        **kwargs
    )
    
    if hasattr(response, 'choices') and len(response.choices) > 0:
        return response.choices[0].message.content
    
    return str(response)


async def simple_llm_call_async(
    prompt: str,
    model: str = "gpt-4o",
    system_message: Optional[str] = None,
    temperature: float = 0.7,
    **kwargs
) -> str:
    """
    Simple async LLM call that returns just the text content
    
    Args:
        prompt: User prompt
        model: Model name
        system_message: Optional system message
        temperature: Sampling temperature
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
    - OPENAI_API_KEY
    - ANTHROPIC_API_KEY
    - AZURE_API_KEY
    - etc.
    """
    # LiteLLM automatically reads from standard environment variables
    # You can also set them programmatically:
    # os.environ["OPENAI_API_KEY"] = "your-key"
    pass


# Initialize on import
configure_llm_api_keys()

print(f"✓ LiteLLM configured with logging to: {LOGS_DIR}")
