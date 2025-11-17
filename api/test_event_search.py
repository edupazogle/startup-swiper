"""
Test script for event search functionality in AI Concierge
"""
import asyncio
from database import SessionLocal
from qwen_agentic_concierge import create_qwen_concierge

async def test_event_searches():
    """Test various event search scenarios"""
    db = SessionLocal()
    concierge = create_qwen_concierge(db)
    
    print("=" * 80)
    print("TESTING AI CONCIERGE EVENT SEARCH CAPABILITIES")
    print("=" * 80)
    
    # Test queries
    queries = [
        "What events is Google hosting at Slush?",
        "Show me AI-related events",
        "What events are happening on Nov 19?",
        "Tell me about the Y Science 2025 event",
        "Which companies are organizing the most events?",
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n{'=' * 80}")
        print(f"TEST {i}: {query}")
        print("=" * 80)
        
        try:
            response = await concierge.answer_question(query)
            print(f"\n{response}\n")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Small delay between tests
        await asyncio.sleep(1)
    
    db.close()
    print("\n" + "=" * 80)
    print("TESTING COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(test_event_searches())
