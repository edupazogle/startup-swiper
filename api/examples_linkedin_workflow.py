#!/usr/bin/env python
"""
LinkedIn Post Generator - Two-Step Workflow
Demonstrates the clarification questions flow
"""

import asyncio
import sys
sys.path.insert(0, '.')

from database import SessionLocal
from ai_concierge import create_concierge


async def step1_clarification():
    """Step 1: User asks to write a LinkedIn post, agent asks clarifying questions"""
    print("\n" + "="*80)
    print("STEP 1: USER ASKS TO WRITE A LINKEDIN POST")
    print("="*80)
    
    db = SessionLocal()
    concierge = create_concierge(db)
    
    user_request = "I want to write a LinkedIn post about AI in insurance"
    print(f"\n👤 User: {user_request}\n")
    
    response = await concierge.answer_question(user_request)
    
    print("🤖 AI Concierge:\n")
    print(response)
    
    return response


async def step2_generate_with_details():
    """Step 2: After user answers questions, generate the full post"""
    print("\n" + "="*80)
    print("STEP 2: USER PROVIDES DETAILS, AGENT GENERATES POST")
    print("="*80)
    
    db = SessionLocal()
    concierge = create_concierge(db)
    
    print("""
👤 User Response to Clarifying Questions:
---
1. Focus: I want to focus on claims processing automation and cost reduction
2. Companies: Mention AXA and how we're leading with AI
3. Tone: Authoritative with stats, we're a thought leader
4. Key points: 40% cost reduction, 10x faster claims, better customer experience
""")
    
    # Generate post with the details provided
    post = await concierge.generate_linkedin_post(
        topic="The AI revolution in insurance claims processing at AXA",
        key_points=[
            "AI claims processing 10x faster than manual review",
            "40% operational cost reduction through automation",
            "Better customer experience with 24/7 chatbot support",
            "AXA leading the charge in InsurTech innovation"
        ],
        people_companies_to_tag=["@AXA", "@InsurTech Leaders"],
        call_to_action="How is AI transforming your insurance operations?",
        link="https://axa.com/ai-innovation"
    )
    
    print("\n🤖 AI Concierge - Generated LinkedIn Post:\n")
    print(post)
    
    return post


async def example_various_topics():
    """Show how clarification works for different topics"""
    print("\n" + "="*80)
    print("BONUS: CLARIFICATION FLOW FOR DIFFERENT TOPICS")
    print("="*80)
    
    db = SessionLocal()
    concierge = create_concierge(db)
    
    topics = [
        "write a linkedin post",
        "help me write a post about our web3 fund",
        "create a linkedin post about slush 2025",
        "generate a post about startup funding trends"
    ]
    
    for i, topic in enumerate(topics, 1):
        print(f"\n--- Example {i}: {topic} ---")
        response = await concierge.answer_question(topic)
        # Just show first few lines of response
        lines = response.split('\n')[:3]
        for line in lines:
            if line.strip():
                print(f"  {line}")
        print("  [... more questions ...]")


async def full_workflow_demo():
    """Run complete workflow demonstration"""
    print("\n" + "🚀"*40)
    print("LINKEDIN POST GENERATOR - INTERACTIVE WORKFLOW DEMO")
    print("🚀"*40)
    
    # Step 1: Ask clarifying questions
    print("\n\n📋 WORKFLOW OVERVIEW:")
    print("""
1. User asks to write a LinkedIn post (with or without a topic)
2. AI Concierge asks clarifying questions about:
   - Topic/focus area
   - Companies/people to mention
   - Key points to include
   - Tone and style
3. User provides details
4. AI Concierge generates a professional LinkedIn post
""")
    
    # Show Step 1
    clarification = await step1_clarification()
    
    # Show Step 2
    post = await step2_generate_with_details()
    
    # Show other examples
    await example_various_topics()
    
    print("\n" + "="*80)
    print("✅ WORKFLOW COMPLETE")
    print("="*80)
    print("""
Key Benefits of This Two-Step Approach:

✅ Ensures all necessary context is gathered before generation
✅ Creates more personalized and relevant posts
✅ Reduces back-and-forth revision
✅ Lets user provide specific details about startups, events, etc.
✅ More engaging and actionable final post

The agent intelligently detects LinkedIn post requests and:
- Asks relevant clarifying questions using NVIDIA NIM
- Gathers context about the topic, companies, and goals
- Generates a polished, professional post with gathered details
- Maintains conversational, helpful tone throughout
""")


if __name__ == "__main__":
    asyncio.run(full_workflow_demo())
