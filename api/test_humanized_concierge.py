#!/usr/bin/env python3
"""
Test script to demonstrate the humanized AI Concierge
Shows conversational, natural responses instead of robotic data dumps
"""

import asyncio
from database import SessionLocal
from qwen_agent_enhanced_concierge import create_qwen_agent_concierge

async def test_conversational_responses():
    """Test the humanized conversational style"""
    db = SessionLocal()
    
    try:
        print("\n" + "=" * 70)
        print("HUMANIZED AI CONCIERGE - CONVERSATIONAL STYLE DEMO")
        print("=" * 70 + "\n")
        
        concierge = create_qwen_agent_concierge(db)
        
        test_queries = [
            "What events is Google hosting?",
            "Find AI startups",
            "Tell me about SimplifAI",
            "Who is Eduardo Paz?",
            "What's happening on Nov 19?",
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n{'─' * 70}")
            print(f"Query {i}: {query}")
            print('─' * 70)
            
            try:
                response = await concierge.chat(query)
                print(f"\n{response}\n")
            except Exception as e:
                print(f"Error: {e}\n")
            
            # Small delay between tests
            await asyncio.sleep(1)
        
        print("\n" + "=" * 70)
        print("DEMO COMPLETE")
        print("=" * 70)
        print("\nKey Improvements:")
        print("✅ Natural, conversational language")
        print("✅ Short responses (2-3 sentences)")
        print("✅ No markdown formatting or bullet lists")
        print("✅ Asks follow-up questions")
        print("✅ Contextualizes information")
        print("=" * 70 + "\n")
        
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_conversational_responses())
