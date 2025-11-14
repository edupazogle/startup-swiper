"""
Example script demonstrating how to use LiteLLM in your Python code

This shows how to use the llm_config module directly without going through the API.
"""

import asyncio
from llm_config import (
    simple_llm_call,
    simple_llm_call_async,
    llm_completion,
    llm_completion_sync
)

def example_1_simple_sync():
    """Example 1: Simple synchronous LLM call"""
    print("\n" + "="*60)
    print("Example 1: Simple Synchronous LLM Call")
    print("="*60)
    
    response = simple_llm_call(
        prompt="Explain what product-market fit means in one sentence.",
        model="gpt-4o-mini",
        temperature=0.7
    )
    
    print(f"Response: {response}")
    print("✓ Log saved to logs/llm/")

async def example_2_simple_async():
    """Example 2: Simple async LLM call"""
    print("\n" + "="*60)
    print("Example 2: Simple Async LLM Call")
    print("="*60)
    
    response = await simple_llm_call_async(
        prompt="What are the top 3 metrics for a SaaS startup?",
        model="gpt-4o-mini",
        system_message="You are a startup advisor. Be concise.",
        temperature=0.5
    )
    
    print(f"Response: {response}")
    print("✓ Log saved to logs/llm/")

async def example_3_chat_conversation():
    """Example 3: Full chat conversation with history"""
    print("\n" + "="*60)
    print("Example 3: Chat with Conversation History")
    print("="*60)
    
    messages = [
        {"role": "system", "content": "You are a helpful startup mentor."},
        {"role": "user", "content": "What is a startup accelerator?"},
    ]
    
    # First response
    response1 = await llm_completion(
        messages=messages,
        model="gpt-4o-mini",
        temperature=0.7
    )
    
    content1 = response1.choices[0].message.content
    print(f"Assistant: {content1}\n")
    
    # Add to conversation history
    messages.append({"role": "assistant", "content": content1})
    messages.append({"role": "user", "content": "What are some famous ones?"})
    
    # Second response with context
    response2 = await llm_completion(
        messages=messages,
        model="gpt-4o-mini",
        temperature=0.7
    )
    
    content2 = response2.choices[0].message.content
    print(f"Assistant: {content2}")
    print("✓ Both messages logged to logs/llm/")

async def example_4_with_metadata():
    """Example 4: LLM call with custom metadata"""
    print("\n" + "="*60)
    print("Example 4: LLM Call with Custom Metadata")
    print("="*60)
    
    response = await llm_completion(
        messages=[
            {"role": "user", "content": "Suggest a startup idea in fintech"}
        ],
        model="gpt-4o-mini",
        temperature=0.9,
        metadata={
            "feature": "idea_generation",
            "user_id": "user_123",
            "session": "abc-def-ghi",
            "category": "fintech"
        }
    )
    
    content = response.choices[0].message.content
    print(f"Response: {content}")
    print("✓ Log includes custom metadata")

def example_5_different_models():
    """Example 5: Using different LLM models"""
    print("\n" + "="*60)
    print("Example 5: Testing Different Models")
    print("="*60)
    
    prompt = "Explain startup equity in simple terms."
    
    models = [
        "gpt-4o-mini",
        "gpt-3.5-turbo",
        # Uncomment if you have Anthropic API key:
        # "claude-3-5-sonnet-20241022",
    ]
    
    for model in models:
        print(f"\n--- Testing {model} ---")
        try:
            response = simple_llm_call(
                prompt=prompt,
                model=model,
                temperature=0.7
            )
            print(f"Response: {response[:100]}...")
            print(f"✓ Success with {model}")
        except Exception as e:
            print(f"✗ Error with {model}: {e}")

async def example_6_streaming():
    """Example 6: Streaming response"""
    print("\n" + "="*60)
    print("Example 6: Streaming Response")
    print("="*60)
    
    print("Streaming: ", end="", flush=True)
    
    async for chunk in llm_completion(
        messages=[
            {"role": "user", "content": "Write a short tagline for a startup marketplace."}
        ],
        model="gpt-4o-mini",
        stream=True
    ):
        if hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end="", flush=True)
    
    print("\n✓ Streaming complete, log saved")

def example_7_error_handling():
    """Example 7: Error handling and logging"""
    print("\n" + "="*60)
    print("Example 7: Error Handling")
    print("="*60)
    
    try:
        # This will fail - invalid model name
        response = simple_llm_call(
            prompt="Test prompt",
            model="invalid-model-name",
        )
    except Exception as e:
        print(f"✓ Caught error: {e}")
        print("✓ Error details logged to logs/llm/")

async def main():
    """Run all examples"""
    print("="*60)
    print("LiteLLM Usage Examples")
    print("="*60)
    print("\nThese examples demonstrate different ways to use LiteLLM.")
    print("All requests and responses are automatically logged to logs/llm/\n")
    
    input("Press Enter to start examples...")
    
    # Run synchronous examples
    example_1_simple_sync()
    
    # Run async examples
    await example_2_simple_async()
    await example_3_chat_conversation()
    await example_4_with_metadata()
    
    # More examples
    example_5_different_models()
    
    # Streaming
    await example_6_streaming()
    
    # Error handling
    example_7_error_handling()
    
    print("\n" + "="*60)
    print("Examples Complete!")
    print("="*60)
    print(f"\nCheck logs/llm/ for all request/response logs")

if __name__ == "__main__":
    # Run async examples
    asyncio.run(main())
